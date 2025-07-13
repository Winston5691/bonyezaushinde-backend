from __future__ import annotations
import random
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.message import MessageDB, MessageOptionDB, MessageDeliveryDB
from app.db.models.game import TicketDB, RoundDB
from app.utils.sms_utils import send_sms

__all__ = ["handle_incoming_sms"]


def _save_outgoing(
    db: Session,
    phone: str,
    text: str,
    status: str,
    msg_id: Optional[str] = None,
    *,
    round_id: Optional[int] = None,
) -> MessageDB:
    out_msg = MessageDB(
        phone_number=phone,
        content=text,
        direction="outgoing_system_response",
        status=status,
        message_id=msg_id,
        timestamp=datetime.utcnow(),
        round_id=round_id,
    )
    db.add(out_msg)
    db.commit()
    db.refresh(out_msg)
    return out_msg


def normalize_phone(phone_number: str) -> str:
    phone_number = phone_number.strip()
    if phone_number.startswith("0"):
        return "+254" + phone_number[1:]
    if phone_number.startswith("254"):
        return "+" + phone_number
    if not phone_number.startswith("+"):
        return "+254" + phone_number
    return phone_number


def generate_next_question_text() -> tuple[str, dict[str, int]]:
    intros = [
        "🎰 Feeling lucky? Choose a pot and reveal your fate:",
        "💥 Hidden prizes await... Pick wisely!",
        "🔥 One choice could change your game! Select a pot:",
        "🎁 Crack open the pot and claim your treasure:",
        "💸 Next round begins! Which pot hides your fortune?"
    ]
    intro = random.choice(intros)
    amounts = random.sample([20, 30, 40, 50], 4)
    choices = ['A', 'B', 'C', 'D']
    text_lines = [f"{ch}. Ksh {amt}" for ch, amt in zip(choices, amounts)]
    options = dict(zip(choices, amounts))
    full_text = f"{intro}\n" + "\n".join(text_lines) + "\nReply with A, B, C, or D"
    return full_text, options


def _create_new_round_and_question(db: Session) -> tuple[RoundDB, MessageDB]:
    round_ = RoundDB(status="open")
    db.add(round_)
    db.commit()
    db.refresh(round_)

    question_text, options = generate_next_question_text()

    question = MessageDB(
        phone_number="system",
        content=question_text,
        direction="outgoing_question",
        status="sent",
        timestamp=datetime.utcnow(),
        round_id=round_.id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    for choice, amount in options.items():
        db.add(MessageOptionDB(message_id=question.id, choice=choice, amount=amount))
    db.commit()

    return round_, question


def handle_incoming_sms(db: Session, phone_number: str, text: str) -> str:
    phone_number = normalize_phone(phone_number)
    reply_text = text.strip().upper()

    # Store inbound SMS
    inbound_msg = MessageDB(
        phone_number=phone_number,
        content=reply_text,
        direction="incoming",
        status="received",
        timestamp=datetime.utcnow(),
    )
    db.add(inbound_msg)
    db.commit()

    # Ensure open round exists
    round_ = db.query(RoundDB).filter(RoundDB.status == "open").first()
    if not round_:
        round_, question = _create_new_round_and_question(db)
        sms_resp = send_sms(phone_number, question.content)
        recs = sms_resp.get("SMSMessageData", {}).get("Recipients", [])
        status = recs[0].get("status") if recs else "Error"
        msg_id = recs[0].get("messageId") if recs else None
        _save_outgoing(db, phone_number, question.content, status, msg_id, round_id=round_.id)
        return "new_round_started"

    # Get latest question in the round
    question = (
        db.query(MessageDB)
        .filter(
            MessageDB.round_id == round_.id,
            MessageDB.direction == "outgoing_question",
        )
        .order_by(MessageDB.timestamp.desc())
        .first()
    )

    # Validate the reply
    option = (
        db.query(MessageOptionDB)
        .filter(
            MessageOptionDB.message_id == question.id,
            MessageOptionDB.choice.ilike(reply_text),
        )
        .first()
    )

    if not option:
        error_text = "❌ Invalid choice. Please reply with A, B, C, or D as shown."
        sms_resp = send_sms(phone_number, error_text)
        recs = sms_resp.get("SMSMessageData", {}).get("Recipients", [])
        status = recs[0].get("status") if recs else "Error"
        msg_id = recs[0].get("messageId") if recs else None
        _save_outgoing(db, phone_number, error_text, status, msg_id, round_id=round_.id)
        return "invalid_choice"

    # Save the ticket
    ticket = TicketDB(
        round_id=round_.id,
        message_id=question.id,
        phone=phone_number,
        choice=reply_text,
        amount=option.amount,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Count tickets
    total_tickets = db.query(TicketDB).filter(TicketDB.message_id == question.id).count()

    if total_tickets % 10 == 0:
        prize = option.amount * 3
        result_text = (
            f"🎉 JACKPOT! You were the 10th player and just WON Ksh {prize:.2f} for picking {reply_text}!"
        )
    else:
        fake_choices = ["A", "B", "C", "D"]
        fake_choices.remove(reply_text)
        fake_winner = random.choice(fake_choices)
        fake_amount = random.randint(300, 10000)
        result_text = (
            f"😢 Not lucky this time. Your choice {reply_text} missed it. "
            f"Winning pot was {fake_winner} worth Ksh {fake_amount}. Try again!"
        )

    # Send result SMS
    sms_resp = send_sms(phone_number, result_text)
    recs = sms_resp.get("SMSMessageData", {}).get("Recipients", [])
    status = recs[0].get("status") if recs else "Error"
    msg_id = recs[0].get("messageId") if recs else None

    confirmation_msg = _save_outgoing(db, phone_number, result_text, status, msg_id, round_id=round_.id)
    db.add(
        MessageDeliveryDB(
            message_id=confirmation_msg.id,
            phone_number=phone_number,
            status=status,
            api_response=str(sms_resp),
        )
    )
    db.commit()

    # Create & send next question
    round_, next_question = _create_new_round_and_question(db)
    sms_resp2 = send_sms(phone_number, next_question.content)
    rec2 = sms_resp2.get("SMSMessageData", {}).get("Recipients", [])
    status2 = rec2[0].get("status") if rec2 else "Error"
    msg_id2 = rec2[0].get("messageId") if rec2 else None

    _save_outgoing(db, phone_number, next_question.content, status2, msg_id2, round_id=round_.id)

    return "reply_processed"
