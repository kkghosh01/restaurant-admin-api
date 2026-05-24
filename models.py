from sqlalchemy import (
    Column, Integer, String,
    DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    address    = Column(String,  nullable=False)
    phone      = Column(String,  nullable=False)
    total      = Column(Integer, nullable=False)
    status     = Column(String,  default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("OrderItem", back_populates="order",
                         cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False,
                            cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    order_id    = Column(Integer, ForeignKey("orders.id"), nullable=False)
    trx_id      = Column(String,  nullable=False)
    phone_last4 = Column(String,  nullable=False)
    amount      = Column(Integer, nullable=False)
    status      = Column(String,  default="pending")
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at  = Column(DateTime, nullable=False)

    order = relationship("Order", back_populates="payment")


class OrderItem(Base):
    __tablename__ = "order_items"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    name     = Column(String,  nullable=False)
    price    = Column(Integer, nullable=False)
    qty      = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String,  nullable=False)
    name     = Column(String,  nullable=False)
    bangla   = Column(String,  nullable=False)  # JSON string
    aliases  = Column(String,  nullable=True)   # JSON string
    price    = Column(Integer, nullable=False)
    active   = Column(Integer, default=1)       # 1=active, 0=hidden

