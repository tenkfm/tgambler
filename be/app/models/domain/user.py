from services.firebase.firebase_object import FirebaseObject
from datetime import datetime
from typing import Optional

class UserInfo(FirebaseObject):
    tg_id: str
    username: str
    first_name: str
    last_name: Optional[str]
    language_code: str
    photo_url: str

    is_premium: bool
    tgWebAppPlatform: str
    tgWebAppVersion: str
    auth_date: datetime
    chat_instance: str
    signature: str

    @staticmethod
    def collection_name():
        return "users"  # Firestore collection for User instances
    
class LaunchInfo(FirebaseObject):
    launch_date: datetime
    tgWebAppPlatform: str

    @staticmethod
    def collection_name():
        return "launch_info"  # Firestore collection for LaunchInfo instances

# Define a Pydantic model for user input
class User(FirebaseObject):
    email: str
    display_name: str

    @staticmethod
    def collection_name():
        return "users"  # Firestore collection for User instances