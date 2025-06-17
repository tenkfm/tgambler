from dotenv import load_dotenv
from functools import lru_cache
from app.settings import Settings
from app.services.firebase.firebase_service import FirebaseService
from app.controllers.user_controller import UserController
from app.controllers.case_controller import CaseController

###
### Load global params
###
@lru_cache()
def get_settings():
    return Settings()

class Container:
    # Services
    firebase_service: FirebaseService

    # Controllers
    user_ctonroller: UserController
    case_controller: CaseController

    def populate(self):
        settings = get_settings()
        firebase_service_account_key = settings.firebase_api_token
        firebase_service = FirebaseService(api_key=firebase_service_account_key)
        self.firebase_service = firebase_service

        self.user_ctonroller = UserController(firebase_service=self.firebase_service)
        self.case_controller = CaseController(firebase_service=self.firebase_service)

container = Container()
container.populate()