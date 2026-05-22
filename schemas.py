from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class OrderItemSchema(BaseModel):
    id    : int
    name  : str
    price : int
    qty   : int

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id         : int
    user_id    : int
    address    : str
    phone      : str
    total      : int
    status     : str
    created_at : datetime
    items      : List[OrderItemSchema]

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str  # pending | preparing | delivered | cancelled


class RevenueStats(BaseModel):
    today_revenue : int
    total_revenue : int
    total_orders  : int
    pending_count : int