import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, Order
from schemas import PaymentSchema

router = APIRouter(prefix="/payments", tags=["payments"])

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ─── Telegram message sender ─────────────────────────
async def send_telegram_message(user_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": user_id,
                "text": text,
            },
        )


# ─── Pending payments ────────────────────────────────
@router.get("/pending", response_model=list[PaymentSchema])
def get_pending_payments(db: Session = Depends(get_db)):
    return (
        db.query(Payment)
        .filter(Payment.status == "pending")
        .order_by(Payment.created_at.desc())
        .all()
    )


# ─── Verify payment ──────────────────────────────────
@router.patch("/{payment_id}/verify")
async def verify_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "confirmed"

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        order.status = "preparing"
        db.commit()

        # ✅ Customer-কে Telegram message পাঠাও
        await send_telegram_message(
            user_id=order.user_id,
            text=(
                f"✅ আপনার payment confirm হয়েছে!\n\n"
                f"📋 Order ID: ORDER-{order.id:04d}\n"
                f"💰 Amount: ৳{order.total}\n\n"
                f"👨‍🍳 আপনার খাবার prepare হচ্ছে।\n"
                f"🚚 30-40 মিনিটে delivery হবে।\n\n"
                f"ধন্যবাদ! 🙏"
            ),
        )
    else:
        db.commit()

    return {"message": "Payment verified", "order_id": payment.order_id}


# ─── Reject payment ──────────────────────────────────
@router.patch("/{payment_id}/reject")
async def reject_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "rejected"

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        db.commit()

        # ✅ Customer-কে rejection message পাঠাও
        await send_telegram_message(
            user_id=order.user_id,
            text=(
                f"❌ আপনার payment verify হয়নি।\n\n"
                f"📋 Order ID: ORDER-{order.id:04d}\n\n"
                f"সম্ভাব্য কারণ:\n"
                f"• ভুল Transaction ID\n"
                f"• ভুল number\n\n"
                f"সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।\n"
                f"সাহায্যের জন্য: 01737-233015"
            ),
        )
    else:
        db.commit()

    return {"message": "Payment rejected"}
