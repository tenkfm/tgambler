from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.services.firebase.firebase_object import FirebaseObject

class Currency(str, Enum):
    TON = "TON"
    COIN = "COIN"
    XTR = "XTR"

class TopUpStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Wallet(FirebaseObject):
    user_id: str
    balance: int = 0
    currency: Currency
    last_updated: Optional[datetime] = None  # Timestamp of the last update

    @staticmethod
    def collection_name():
        return "wallets"

class Transaction(FirebaseObject):
    from_wallet_id: str  # ID of the wallet initiating the transaction
    to_wallet_id: str  # ID of the wallet receiving the transaction
    amount: int # Amount of the transaction in cents
    currency: Currency  # Currency of the transaction
    timestamp: datetime = datetime.now()  # Timestamp of the transaction
    description: str  # Description of the transaction

    @staticmethod
    def collection_name():
        return "transactions"

class TopUpRequest(FirebaseObject):
    user_id: str
    amount: int # In cents
    provider: str
    currency: Currency
    external_id: str
    status: TopUpStatus
    payload: Optional[str] = None
    info: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()

    @staticmethod
    def collection_name():
        return "topup_requests"
