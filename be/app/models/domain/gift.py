from services.firebase.firebase_object import FirebaseObject
from datetime import datetime
from typing import Optional

class Gift(FirebaseObject):
    case_id: str
    name: str
    image_url: str
    background: str
    cost: int
    is_active: bool
    
    @staticmethod
    def collection_name():
        return "gifts"  # Firestore collection for User instances