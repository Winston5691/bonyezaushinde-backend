from fastapi import APIRouter, Depends, HTTPException,  Request, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.message import MessageSend
from app.services.sms_service import broadcast_message
from app.services.incoming_sms_service import handle_incoming_sms

router = APIRouter(prefix="/sms", tags=["Incoming SMS"])

router = APIRouter()

@router.post("/send")
def send_bulk_message(
    payload: MessageSend,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    results = broadcast_message(db, payload.content, [opt.dict() for opt in payload.options])

    failed = [r for r in results if not r.get("success")]
    if failed:
        raise HTTPException(status_code=500, detail={
            "message": "Some messages failed to send",
            "failures": failed
        })

    return {"detail": "All messages sent successfully"}


@router.post("/incoming", status_code=status.HTTP_200_OK)
async def receive_sms(request: Request, db: Session = Depends(get_db)):
    """Africa's Talking will POST: text, from, to, date, etc."""
    form = await request.form()
    phone_number = form.get("from") or form.get("fromNumber")
    text = form.get("text") or form.get("message")

    if not phone_number or not text:
        return {"detail": "Invalid payload"}

    result = handle_incoming_sms(db, phone_number, text)
    return {"detail": result}
