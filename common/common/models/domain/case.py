from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from common.services.firebase.firebase_object import FirebaseObject
from common.models.domain.gift import GiftType

class CaseOpeningStatus(str, Enum):
    NEW = "NEW"
    REDEPED = "REDEPED"
    INVENTORY = "INVENTORY"

class Case(FirebaseObject):
    name: str
    cost: int
    image_url: str
    is_active: bool
    
    @staticmethod
    def collection_name():
        return "cases"  # Firestore collection for User instances
    
    @property
    def costf(self) -> float:
        """
        Calculate the cost as a float.
        :return: Cost as a float.
        """
        return self.cost / 100.0 if self.cost else 0.0
    
class CaseOpening(FirebaseObject):
    user_id: str
    case_id: str
    gift_id: str
    gift_type: GiftType
    gift_volume: int
    status: CaseOpeningStatus
    open_at: datetime

    @property
    def gift_volumef(self) -> float:
        """
        Calculate the gift volume as a float.
        """
        return self.gift_volume / 100.0 if self.gift_volume else 0.0

    @staticmethod
    def collection_name():
        return "case_openings"  # Firestore collection for User instances

class CaseInfo(BaseModel):
    id: str
    name: str
    cost: int
    is_valid: bool
    description: str
    rtp: float
