from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, field_validator
from common.services.firebase.firebase_object import FirebaseObject

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
    
    @field_validator('currency', mode='before')
    def _normalize_currency(cls, v):
        """
        Если из Firestore пришло "Currency.COIN", обрезаем префикс.
        Иначе передаём значение дальше (Pydantic сам сконвертирует
        строку 'COIN' в Currency.COIN).
        """
        if isinstance(v, str) and v.startswith(f"{Currency.__name__}."):
            return v.split(".", 1)[1]
        return v

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
    
    @field_validator('currency', mode='before')
    def _normalize_currency(cls, v):
        if isinstance(v, str) and v.startswith(f"{Currency.__name__}."):
            return v.split(".", 1)[1]
        return v

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