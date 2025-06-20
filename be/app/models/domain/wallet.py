from enum import Enum
from typing import Optional
from datetime import datetime
from app.services.firebase.firebase_object import FirebaseObject

class Currency(str, Enum):
    TON = "TON"
    COIN = "COIN"

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
    timestamp: datetime = datetime.now()  # Timestamp of the transaction
    description: str  # Description of the transaction

    @staticmethod
    def collection_name():
        return "transactions"  # Firestore collection for Transaction instances