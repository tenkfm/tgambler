from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from common.services.firebase.firebase_object import FirebaseObject

class GiftType(str, Enum):
    PORTALS_GIFT = "PORTALS_GIFT"
    BALANCE = "BALANCE"

class Attribute(BaseModel):
    type: str
    value: str
    rarity_per_mille: float

class PortalsNFT(BaseModel):
    id: str
    tg_id: str
    collection_id: str
    external_collection_number: int
    name: str
    photo_url: str
    price: Optional[str] = None
    attributes: Optional[List[Attribute]] = []
    listed_at: Optional[str] = None
    status: Optional[str] = None
    animation_url: Optional[str] = None
    emoji_id: Optional[str] = None
    has_animation: Optional[bool] = None
    floor_price: Optional[str] = None
    unlocks_at: Optional[str] = None
    is_owned: Optional[bool] = None

    @property
    def pricef(self) -> float:
        try:
            return float(self.price) if self.price is not None else 0.0
        except ValueError:
            return 0.0
        
class TONReward(BaseModel):
    id: str
    name: str
    volume: int
    photo_url: str

class Gift(FirebaseObject):
    case_id: str
    name: str
    prob: int
    volume: int
    is_active: bool
    type: GiftType

    payload: PortalsNFT | TONReward = None

    @property
    def probf(self) -> float:
        """
        Calculate the probability as a percentage.
        :return: Probability as a float between 0 and 1.
        """
        return self.prob / 100.0 if self.prob else 0.0
    
    @property
    def volumef(self) -> float:
        """
        Calculate the probability as a percentage.
        :return: Probability as a float between 0 and 1.
        """
        return self.volume / 100.0 if self.volume else 0.0
    
    def update_payload(self, payload: PortalsNFT | TONReward):
        """
        Update the payload of the gift.
        :param payload: The new payload to set.
        """
        if isinstance(payload, (PortalsNFT)):
            self.volume = int(float(payload.price) * 100)
            self.payload = payload
            
        elif isinstance(payload, TONReward):
            self.volume = payload.volume
            self.payload = payload
        else:
            raise ValueError("Payload must be an instance of PortalsNFT or TONReward.")
    
    @staticmethod
    def collection_name():
        return "gifts"  # Firestore collection for User instances