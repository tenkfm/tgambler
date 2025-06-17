from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: int
    amount: float
    order_id: int
    currency: str
    status: str
    created_at: Optional[datetime] = None

class InvoiceRequest(BaseModel):
    th_id: int
    amount: float