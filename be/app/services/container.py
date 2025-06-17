import os
from dotenv import load_dotenv
from fastapi import Depends
from models.domain.user import User
from services.firebase.firebase_service import FirebaseService
from controllers.user_controller import UserController

class Container:
    # Services
    firebase_service: FirebaseService

    # Controllers
    user_ctonroller: UserController

    def populate(self):
        load_dotenv()
        firebase_service_account_key = os.getenv("FIREBASE_API_TOKEN")
        firebase_service = FirebaseService(api_key=firebase_service_account_key)
        self.firebase_service = firebase_service

        self.user_ctonroller = UserController(firebase_service=self.firebase_service)

container = Container()
container.populate()