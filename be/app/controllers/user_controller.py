from fastapi import HTTPException, Depends
from datetime import datetime

from controllers.base_controller import BaseController
from services.firebase.firebase_service import FirebaseService
from google.cloud.firestore_v1.base_query import FieldFilter

from models.domain.user import UserInfo, LaunchInfo

class UserController(BaseController):
    _firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService = Depends(FirebaseService)):
        self._firebase_service = firebase_service

    def on_launch(self, user: UserInfo):
        """
        On application launch we want to create/update user id and info in the database.
        """
        try:
             # Check if user exists
            users = self._firebase_service.fetch_all(
                model_class=UserInfo,
                filters=[FieldFilter("tg_id", "==", user.tg_id)]
            )

            if users and users.__len__() > 0:
                  # Get the first user if exists
                self.__update_user_on_launch(user, users[0].id)
                return {"status": "ok"}
            else:
                # User not found, create a new user
                self.__create_user_on_launch(user)
                return {"status": "ok"}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
    
    def __create_user_on_launch(self, user: UserInfo):
        self._firebase_service.add(user)
        self.__save_launch_info(user)

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
        print(f"Launch info saved for user {user_id} - {launchInfo}")