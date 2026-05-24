from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class OrderItemSchema(BaseModel):
    id: int
    name: str
    price: int
    qty: int

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    user_id: int
    address: str
    phone: str
    total: int
    status: str
    created_at: datetime
    items: List[OrderItemSchema]

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str  # pending | preparing | delivered | cancelled


class RevenueStats(BaseModel):
    today_revenue: int
    total_revenue: int
    total_orders: int
    pending_count: int


class PaymentSchema(BaseModel):
    id: int
    order_id: int
    trx_id: str
    phone_last4: str
    amount: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MenuItemResponse(BaseModel):
    id: int
    category: str
    name: str
    bangla: List[str]
    aliases: Optional[List[str]] = []
    price: int
    active: int

    class Config:
        from_attributes = True


class UpdatePriceRequest(BaseModel):
    price: int


class CreateMenuItemRequest(BaseModel):
    name: str
    category: str
    price: int
    bangla: List[str]
    active: int = 1


class UpdateActiveRequest(BaseModel):
    active: int

