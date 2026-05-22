from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, date
from database import get_db
from models import Order, OrderItem
from schemas import OrderSchema, StatusUpdate, RevenueStats

router = APIRouter(prefix="/orders", tags=["orders"])


# ─── সব orders ───────────────────────────────────────
@router.get("/", response_model=list[OrderSchema])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()


# ─── একটা order ──────────────────────────────────────
@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ─── Status update ───────────────────────────────────
@router.patch("/{order_id}/status", response_model=OrderSchema)
def update_status(order_id: int, body: StatusUpdate,
                  db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    VALID = {"pending", "preparing", "delivered", "cancelled"}
    if body.status not in VALID:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {VALID}")

    order.status = body.status
    db.commit()
    db.refresh(order)
    return order


# ─── Revenue stats ───────────────────────────────────
@router.get("/stats/revenue", response_model=RevenueStats)
def get_revenue(db: Session = Depends(get_db)):
    today = date.today()

    today_revenue = db.query(func.sum(Order.total)).filter(
        func.date(Order.created_at) == today,
        Order.status != "cancelled"
    ).scalar() or 0

    total_revenue = db.query(func.sum(Order.total)).filter(
        Order.status != "cancelled"
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).scalar() or 0

    pending_count = db.query(func.count(Order.id)).filter(
        Order.status == "pending"
    ).scalar() or 0

    return RevenueStats(
        today_revenue=today_revenue,
        total_revenue=total_revenue,
        total_orders=total_orders,
        pending_count=pending_count,
    )