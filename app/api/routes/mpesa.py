# app/api/routes/mpesa.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment
from app.models.customer import Customer
from app.core.deps import get_db
from app.services.winner_service import check_if_customer_wins  # ✅ Import it

router = APIRouter()

@router.post("/mpesa/confirmation")
async def mpesa_confirmation(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    # Extract data from Safaricom
    msisdn = data.get("MSISDN")
    amount = float(data.get("TransAmount"))

    # Normalize phone number
    phone = msisdn
    if phone.startswith("254"):
        phone = "+" + phone

    # Save payment to DB
    payment = Payment(
        transaction_type=data.get("TransactionType"),
        trans_id=data.get("TransID"),
        trans_time=data.get("TransTime"),
        trans_amount=amount,
        business_short_code=data.get("BusinessShortCode"),
        bill_ref_number=data.get("BillRefNumber"),
        invoice_number=data.get("InvoiceNumber"),
        org_account_balance=data.get("OrgAccountBalance"),
        msisdn=phone,
        first_name=data.get("FirstName"),
        middle_name=data.get("MiddleName"),
        last_name=data.get("LastName"),
    )
    db.add(payment)
    db.commit()

    # 🔍 Find customer if exists
    customer = db.query(Customer).filter(Customer.phone_number == phone).first()

    # 🏆 Run winner logic
    if customer:
        check_if_customer_wins(db, customer.id, amount)

    return {
        "ResultCode": 0,
        "ResultDesc": "Success"
    }
