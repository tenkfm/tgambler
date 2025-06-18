from fastapi import HTTPException, Depends
from datetime import datetime
import jwt
from google.cloud.firestore_v1.base_query import FieldFilter
from app.models.domain.user import UserInfo, LaunchInfo
from app.models.domain.wallet import Wallet
from app.controllers.base_controller import BaseController
from app.services.firebase.firebase_service import FirebaseService
from app.settings import Settings

class UserController(BaseController):
    _firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService = Depends(FirebaseService)):
        self._firebase_service = firebase_service

    def on_launch(self, user: UserInfo):
        """
        On application launch we want to create/update user id and info in the database.
        Generate jwt token for the user and return it.
        """

        #TODO: Add hash validation for user data
        # key1=value1\nkey2=value2\n...
        # secret_key = HMAC-SHA256(bot_token, "WebAppData")
        # hash == HMAC_SHA256(secret_key, data_string)

        try:
             # Check if user exists
            users = self._firebase_service.fetch_all(
                model_class=UserInfo,
                filters=[FieldFilter("tg_id", "==", user.tg_id)]
            )

            if users and users.__len__() > 0:
                  # Get the first user if exists
                self.__update_user_on_launch(user, users[0].id)
                # Generate a JWT token
                token = self.__generate_jwt(user_id=users[0].id)
                return {"access_token": token}
            else:
                # User not found, create a new user
                new_user_id = self.create_user(user)
                # Generate a JWT token
                token = self.__generate_jwt(user_id=new_user_id)
                return {"access_token": token}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
        
    def validate_token(self, token: str) -> str:
        decoded = jwt.decode(token, Settings().auth_secret_key, algorithms=["HS256"])
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id

    def set_referral_user(self, user_id: str, ref_id: str):
        """
        Set the referral user based on the provided referral ID.
        """

        #TODO: move to redis cache

        user = self._firebase_service.fetch_by_id(
            model_class=UserInfo,
            doc_id=user_id
        )
        
        # Save Referral object
        user.referral_id = ref_id
        self._firebase_service.update(
            id=user_id,
            obj=user
        )
        return {"status": "ok"}
    
    def create_user(self, user: UserInfo) -> str:
        # Create user
        user = self._firebase_service.add(user)
        user_doc_id = user.id
        self.__save_launch_info(user, user_doc_id)

        self._create_wallet(user_doc_id)
        return user_doc_id
    

    # Private methods

    def _create_wallet(self, user_id: str):
        """
        Create a wallet for the user.
        """
        wallet = Wallet(
            user_id=user_id,
            balance=0,
            currency="TON",
            last_updated=datetime.now()
        )
        return self._firebase_service.add(wallet)


    def __generate_jwt(self, user_id: str):
        return jwt.encode({"user_id": user_id}, Settings().auth_secret_key, algorithm="HS256")

    def __update_user_on_launch(self, user: UserInfo, user_id: str):
        self._firebase_service.update(
            id=user_id,
            obj=user
        )
        self.__save_launch_info(user, user_id)

    def __save_launch_info(self, user: UserInfo, user_id: str):
        launchInfo = LaunchInfo(launch_date=datetime.now(), tgWebAppPlatform=user.tgWebAppPlatform)

        self._firebase_service.add_to_subcollection(
            UserInfo,
            user_id,
            launchInfo
        )