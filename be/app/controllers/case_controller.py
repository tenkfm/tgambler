from fastapi import HTTPException, Depends
from datetime import datetime

from controllers.base_controller import BaseController
from services.firebase.firebase_service import FirebaseService
from google.cloud.firestore_v1.base_query import FieldFilter

from models.domain.case import *
from models.domain.gift import *

class CaseController(BaseController):
    _firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService = Depends(FirebaseService)):
        self._firebase_service = firebase_service

    def get_active_cases(self) -> list[Case]:
        return self._firebase_service.fetch_all(
            model_class=Case,
            filters=[FieldFilter("is_active", "==", True)]
        )
    
    def get_gifts(self, case_id: str) -> list[Gift]:
        return self._firebase_service.fetch_all(
            model_class=Gift,
            filters=[
                FieldFilter("is_active", "==", True),
                FieldFilter("case_id", "==", case_id)
            ]
        )