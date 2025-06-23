from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from fastapi import HTTPException, Depends
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter
from app.controllers.base_controller import BaseController
from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.user import UserInfo, LaunchInfo
from common.models.domain.wallet import Wallet, Currency
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

        # Check if user exists
        db_user = self._firebase_service.fetch_one(
            model_class=UserInfo,
            filters=[FieldFilter("tg_id", "==", user.tg_id)]
        )

        if db_user:
                # Get the first user if exists
            self.__update_user_on_launch(db_user, db_user.id)
            # Generate a JWT token
            token = self.__generate_jwt(user_id=db_user.id)
            return {"access_token": token}
        else:
            # User not found, create a new user
            new_user_id = self.create_user(user)
            # Generate a JWT token
            token = self.__generate_jwt(user_id=new_user_id)
            return {"access_token": token}
        
    def validate_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                Settings().auth_secret_key,
                algorithms=["HS256"]
            )
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
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

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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

        self.__create_wallets(user_doc_id)
        return user_doc_id
    

    # Private methods

    def __create_wallets(self, user_id: str):
        """
        Create user's TON wallet.
        """
        ton_wallet = Wallet(
            user_id=user_id,
            balance=0,
            currency=Currency.TON,
            last_updated=datetime.now()
        )
        self._firebase_service.add(ton_wallet)
        
        """
        Create user's COIN wallet.
        """
        coin_wallet = Wallet(
            user_id=user_id,
            balance=0,
            currency=Currency.COIN,
            last_updated=datetime.now()
        )
        self._firebase_service.add(coin_wallet)

        """
        Create user's XTR wallet.
        """
        coin_wallet = Wallet(
            user_id=user_id,
            balance=0,
            currency=Currency.XTR,
            last_updated=datetime.now()
        )
        self._firebase_service.add(coin_wallet)

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