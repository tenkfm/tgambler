from common.services.firebase.firebase_object import FirebaseObject

class Inventory(FirebaseObject):
    user_id: str
    gift_id: str
    volume_fixation: int
    created_at: str
    
    @staticmethod
    def collection_name():
        return "inventory"  # Firestore collection for User instances