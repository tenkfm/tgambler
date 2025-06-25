from dotenv import load_dotenv
from functools import lru_cache
from settings import Settings
from common.services.firebase.firebase_service import FirebaseService

###
### Load global params
###
@lru_cache()
def get_settings():
    return Settings()

class Container:
    # Services
    firebase_service: FirebaseService

    def populate(self):
        settings = get_settings()
        firebase_service_account_key = settings.firebase_api_token
        firebase_service = FirebaseService(api_key=firebase_service_account_key)
        self.firebase_service = firebase_service

container = Container()
container.populate()