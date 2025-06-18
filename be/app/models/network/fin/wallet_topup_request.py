from typing import Optional
from datetime import datetime
from app.services.firebase.firebase_object import FirebaseObject
from pydantic import BaseModel

class WalletTopupRequest(BaseModel):
    amount: int  # Amount to be topped up in cents
    description: str  # Description of the top-up request