from services.firebase.firebase_object import FirebaseObject
from datetime import datetime
from typing import Optional

class Gift(FirebaseObject):
    case_id: str
    name: str
    image_url: str
    background: str
    volume: int
    prob: int
    is_active: bool

    def probf(self) -> float:
        """
        Calculate the probability as a percentage.
        :return: Probability as a float between 0 and 1.
        """
        return self.prob / 100.0 if self.prob else 0.0
    
    def volumef(self) -> float:
        """
        Calculate the probability as a percentage.
        :return: Probability as a float between 0 and 1.
        """
        return self.volume / 100.0 if self.volume else 0.0
    
    @staticmethod
    def collection_name():
        return "gifts"  # Firestore collection for User instances