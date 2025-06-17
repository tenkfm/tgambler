from services.firebase.firebase_object import FirebaseObject
from datetime import datetime
from typing import Optional

class Case(FirebaseObject):
    name: str
    cost: int
    image_url: str
    is_active: bool
    
    @staticmethod
    def collection_name():
        return "cases"  # Firestore collection for User instances