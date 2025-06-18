import random
from bisect import bisect
from datetime import datetime
from functools import reduce
from fastapi import HTTPException, Depends
from google.cloud.firestore_v1.base_query import FieldFilter

from app.controllers.base_controller import BaseController
from app.services.firebase.firebase_service import FirebaseService
from app.controllers.fin_controller import FinController
from app.models.domain.case import *
from app.models.domain.gift import *

class CaseController(BaseController):
    _firebase_service: FirebaseService
    _fin_controller: FinController

    def __init__(
            self,
            firebase_service: FirebaseService = Depends(FirebaseService),
            fin_controller: FinController = Depends(FinController)
        ):
        self._firebase_service = firebase_service
        self._fin_controller = fin_controller

    def get_active_cases(self) -> list[Case]:
        """
        Fetch all active cases from the database.
        :return: A list of Case objects that are currently active.
        """

        return self._firebase_service.fetch_all(
            model_class=Case,
            filters=[FieldFilter("is_active", "==", True)]
        )
    
    def get_case_by_id(self, case_id: str) -> Case:
        """
        Fetch a specific case by its ID.
        :param case_id: The ID of the case to fetch.
        :return: A Case object if found, otherwise raises an HTTPException.
        """
        
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        case = self._firebase_service.fetch_by_id(model_class=Case, doc_id=case_id)
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return case
    
    def get_case_gifts(self, case_id: str) -> list[Gift]:
        """
        Fetch all active gifts for a specific case.
        :param case_id: The ID of the case for which to fetch gifts.
        :return: A list of Gift objects associated with the specified case.
        """

        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        return self._firebase_service.fetch_all(
            model_class=Gift,
            filters=[
                FieldFilter("is_active", "==", True),
                FieldFilter("case_id", "==", case_id)
            ]
        )
    
    def add_gift(self, case_id: str, gift: Gift) -> Gift:
        """
        Add a new gift to the specified case.
        
        :param case_id: The ID of the case to which the gift belongs.
        :param
        gift: The Gift object to be added.
        :return: The added Gift object with its ID.
        """
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")

        try:
            # Set the case_id for the gift
            gift.case_id = case_id
            
            # Add the gift to Firestore
            added_gift = self._firebase_service.add(gift)
            return added_gift
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))


    def open_case(self, user_id: str, case_id: str) -> Gift:
        """
        Open a case and return a random gift from it.
        
        :param case_id: The ID of the case to open.
        :return: A Gift object representing the opened gift.
        """
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        case = self.get_case_by_id(case_id)
        if not case.is_active:
            raise HTTPException(status_code=400, detail="Case is not active")
        
        # Transfer funds from user to app
        self._fin_controller.transfer_funds_from_user_to_app(
            user_id=user_id,
            amount=case.cost,
            description=f"Opening case {case_id}, cost: {case.cost} TON"
        )

        gifts = self.get_case_gifts(case_id)
        gifts.sort(key=lambda gift: gift.prob, reverse=True)

        # Calculate cumulative probabilities
        cum_probs = []
        running = 0
        for gift in gifts:
            running += gift.prob
            cum_probs.append(running)

        r = int(random.random() * 100 * 100)
        print(r)
        idx = bisect(cum_probs, r)
        prize = gifts[idx]

        # Save CaseOpening record
        case_opening = CaseOpening(
            user_id=user_id,
            case_id=case_id,
            gift_id=prize.id,
            gift_type=prize.type,
            gift_volume=prize.volume,
            status=CaseOpeningStatus.NEW,
            open_at=datetime.now()
        )
        self._firebase_service.add(case_opening)
        return case_opening
    

    def get_case_info(self, case: Case) -> CaseInfo:
        """
        Get detailed information about a case, including its gifts.
        
        :param case: The Case object for which to fetch information.
        :return: A CaseInfo object containing the case details and its gifts.
        """
        if not case:
            raise HTTPException(status_code=400, detail="Case is required")
        
        gifts = self.get_case_gifts(case.id)

        case_info = CaseInfo(
            id=case.id,
            name=case.name,
            cost=case.cost,
            is_valid=True,
            description="",
            rtp=0.0
        )

        if not gifts:
            case_info.is_valid = False
            case_info.description = "No gifts available for this case"
            return case_info
        
        prob_sum = reduce(lambda acc, gift: acc + gift.prob, gifts, 0)
        prob_sum = prob_sum / 100
        if prob_sum != 100:
            case_info.is_valid = False
            case_info.description = f"Gift probabilities do not sum to 1, now: {prob_sum}"
            return case_info
        
        # RTP
        sum = reduce(lambda acc, gift: acc + (gift.probf() * gift.volumef()), gifts, 0)
        rtp = sum / case.costf() / 100
        case_info.rtp = round(rtp, 3)

        return case_info
    
    def redep_openning(self, openning_id: str, user_id: str):
        """
        Redeem an existing case opening by topping up the user's balance with the opened gift volume.
        
        :param openning_id: The ID of the case opening to redeem.
        :param user_id: The ID of the user redeeming the opening.
        :return: A message indicating the success of the operation.
        """
        if not openning_id:
            raise HTTPException(status_code=400, detail="Openning ID is required")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        print(openning_id)
        case_opening = self._firebase_service.fetch_by_id(model_class=CaseOpening, doc_id=openning_id)
        
        if not case_opening:
            raise HTTPException(status_code=404, detail="Case opening not found")
        
        if case_opening.status != CaseOpeningStatus.NEW:
            raise HTTPException(status_code=400, detail="Only new case openings can be redeped")
        
        if case_opening.user_id != user_id:
            raise HTTPException(status_code=403, detail="You can only redep your own case openings")
        
        # Transfer gift volume to user
        self._fin_controller.transfer_funds_from_app_to_user(
            user_id=user_id,
            amount=case_opening.gift_volume,
            description=f"Redeeming case opening {openning_id}, gift volume: {case_opening.gift_volume} TON"
        )
        
        # Update case opening status
        case_opening.status = CaseOpeningStatus.REDEPED
        self._firebase_service.update(id=case_opening.id, obj=case_opening)
        
        return {"status": "ok"}