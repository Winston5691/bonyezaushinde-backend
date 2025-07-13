# app/services/winner_service.py

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import random
from app.models.payment import Payment


def check_if_customer_wins(db: Session, msisdn: str, amount: float):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    # Get all payments in the last hour
    recent_payments = db.query(Payment).filter(
        Payment.received_at >= one_hour_ago,
    ).all()

    total_amount = sum(p.trans_amount for p in recent_payments)
    # Get unique players by phone number
    unique_players = list({p.msisdn: p for p in recent_payments if p.msisdn}.values())
    player_count = len(unique_players)

    print(f"⏱️ Total collected in last 1hr: {total_amount}")
    print(f"👥 Unique players in last 1hr: {player_count}")

    if total_amount >= 10000 and player_count >= 5:
        print("💰 Tier Jackpot: 10K+ collected, 5 winners!")
        total_pool = round(total_amount * 0.3)
        winners = random.sample(unique_players, min(5, player_count))
        for winner in winners:
            prize = round(total_pool / len(winners))
            announce_winner(winner.msisdn, prize)

    elif total_amount >= 1000 and player_count >= 3:
        print("🏆 Tier 1: Jackpot Triggered!")
        winners = random.sample(unique_players, min(3, player_count))
        for winner in winners:
            recent = get_latest_payment(db, winner.msisdn)
            prize = round(min(recent.trans_amount * 1.7, 300))
            announce_winner(winner.msisdn, prize)

    elif player_count >= 10:
        print("🥈 Tier 2: Popular Round!")
        winners = random.sample(unique_players, 2)
        for winner in winners:
            recent = get_latest_payment(db, winner.msisdn)
            prize = round(min(recent.trans_amount * 1.5, 200))
            announce_winner(winner.msisdn, prize)

    elif player_count >= 5:
        print("🥉 Tier 3: Small Win Round")
        winner = random.choice(unique_players)
        recent = get_latest_payment(db, winner.msisdn)
        prize = round(min(recent.trans_amount * 1.2, 150))
        announce_winner(winner.msisdn, prize)

    elif player_count >= 3:
        print("🪙 Tier 4: Consolation Reward")
        winner = random.choice(unique_players)
        recent = get_latest_payment(db, winner.msisdn)
        prize = round(recent.trans_amount)
        announce_winner(winner.msisdn, prize)

    elif customer_has_multiple_payments_today(db, msisdn, count=3):
        print("🎁 Loyalty Bonus!")
        bonus = round(amount * 1.1)
        announce_winner(msisdn, bonus)

    else:
        print("⚠️ No reward this time — keep playing!")


def get_latest_payment(db: Session, msisdn: str) -> Payment:
    return db.query(Payment).filter(
        Payment.msisdn == msisdn,
    ).order_by(Payment.received_at.desc()).first()


def customer_has_multiple_payments_today(db: Session, msisdn: str, count: int = 3) -> bool:
    today = datetime.utcnow().date()
    payments_today = db.query(Payment).filter(
        Payment.msisdn == msisdn,
        func.date(Payment.received_at) == today
    ).count()
    return payments_today >= count


def announce_winner(msisdn: str, amount: float):
    print(f"🎉 WINNER ALERT: {msisdn} won KES {amount}")
    # TODO: Save to winners table or send SMS
