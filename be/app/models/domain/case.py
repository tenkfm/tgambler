from fastapi import Depends

from services.firebase.firebase_object import FirebaseObject
from pydantic import BaseModel

class Case(FirebaseObject):
    name: str
    cost: int
    image_url: str
    is_active: bool
    
    @staticmethod
    def collection_name():
        return "cases"  # Firestore collection for User instances
    
    def costf(self) -> float:
        """
        Calculate the cost as a float.
        :return: Cost as a float.
        """
        return self.cost / 100.0 if self.cost else 0.0
    

class CaseInfo(BaseModel):
    id: str
    name: str
    cost: int
    is_valid: bool
    description: str
    rtp: float