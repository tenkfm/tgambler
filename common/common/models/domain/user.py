from typing import Optional
from datetime import datetime
from common.services.firebase.firebase_object import FirebaseObject

class UserInfo(FirebaseObject):
    tg_id: int
    username: str
    first_name: str
    last_name: Optional[str] = None
    language_code: str
    photo_url: str

    is_premium: bool
    tgWebAppPlatform: str
    tgWebAppVersion: str
    auth_date: datetime
    chat_instance: str
    signature: str
    referral_id: str = ""  # Optional field for referral ID (The user who referred this user)

    @staticmethod
    def collection_name():
        return "users"  # Firestore collection for User instances
    
class LaunchInfo(FirebaseObject):
    launch_date: datetime
    tgWebAppPlatform: str

    @staticmethod
    def collection_name():
        return "launch_info"  # Firestore collection for LaunchInfo instances