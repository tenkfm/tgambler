from typing import List, Dict, Optional
from pydantic import BaseModel
from common.services.firebase.firebase_object import FirebaseObject

class PortalsCollection(FirebaseObject):
    portals_id: str
    name: str
    short_name: str
    photo_url: str
    day_volume: str
    volume: str
    floor_price: str
    supply: int

    def merge(self, nft):
        """
        Заменяет все поля текущего объекта значениями другого объекта,
        кроме поля 'id'.
        """
        for key, value in vars(nft).items():
            if key != 'id' and key != 'portals_id':
                setattr(self, key, value)

    @staticmethod
    def collection_name():
        return "portals_collection"

class CollectionAPIResponse(BaseModel):
    collections: List[PortalsCollection]
    floor_changes: Dict[str, str]

class Attribute(BaseModel):
    type: str
    value: str
    rarity_per_mille: float

class PortalsNFT(FirebaseObject):
    class Config:
        extra = "allow"

    portals_id: str
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

    def merge(self, nft):
        """
        Заменяет все поля текущего объекта значениями другого объекта,
        кроме поля 'id'.
        """
        for key, value in vars(nft).items():
            if key != 'id' and key != 'portals_id':
                setattr(self, key, value)

    @staticmethod
    def collection_name():
        return "portals_nft"

class NFTResponse(BaseModel):
    results: List[PortalsNFT]
    total_count: int