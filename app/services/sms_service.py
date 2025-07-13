# FILE: app/services/sms_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.game import RoundDB
from app.db.models.message import (
    MessageDB as Message,
    MessageOptionDB as MessageOption,
    MessageDeliveryDB as MessageDelivery,
)
from app.models.customer import Customer
from app.utils.sms_utils import send_sms


def broadcast_message(db: Session, question: str, options: list[dict]) -> list[dict]:
    """
    Send question + options to all customers.
    Returns a list of dicts: {phone, success, status, error?}
    """
    # ── 0️⃣ create round ───────────────────────────────────────────
    round_obj = RoundDB(question=question, status="open", opened_at=datetime.utcnow())
    db.add(round_obj)
    db.commit()  # commit now to unlock DB
    db.refresh(round_obj)

    customers = db.query(Customer).all()
    results: list[dict] = []

    # ── 1️⃣ loop customers ─────────────────────────────────────────
    for cust in customers:
        sms_text = question + "\n" + "\n".join(
            f"{o['choice']} = Ksh{o['amount']}" for o in options
        )

        # call Africa's Talking
        resp = send_sms(cust.phone_number, sms_text)
        recipients = resp.get("SMSMessageData", {}).get("Recipients", [])

        if not recipients:  # ❌ failed
            results.append({
                "phone": cust.phone_number,
                "success": False,
                "status": "Error",
                "error": resp.get("error", "No recipient returned"),
            })
            continue

        r = recipients[0]  # Africa's Talking always returns one per send

        # ── 1a save message row ────────────────────────────────
        msg = Message(
            customer_id=cust.phone_number,
            phone_number=cust.phone_number,
            content=question,
            direction="outgoing_question",
            status=r.get("status"),               # e.g. 'Success' / 'Queued'
            message_id=r.get("messageId"),
            round_id=round_obj.id,
        )
        db.add(msg)
        db.flush()  # allocate msg.id

        # store options
        for o in options:
            db.add(MessageOption(
                message_id=msg.id,
                choice=o["choice"],
                amount=o["amount"],
                message_text=question,
            ))

        # delivery log
        db.add(MessageDelivery(
            message_id=msg.id,
            phone_number=cust.phone_number,
            status=r.get("status"),
            api_response=str(r),
        ))

        # result entry
        results.append({
            "phone": cust.phone_number,
            "success": r.get("status") == "Success",
            "status": r.get("status"),
        })

    db.commit()   # one commit for all inserts
    return results
