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


    def open_case(self, case_id: str) -> Gift:
        """
        Open a case and return a random gift from it.
        
        :param case_id: The ID of the case to open.
        :return: A Gift object representing the opened gift.
        """
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        self._fin_controller.process_transaction(
            from_wallet_id="user_wallet_id",  # Replace with actual user wallet ID
            to_wallet_id="case_wallet_id",  # Replace with actual case wallet ID
            amount=100,  # Replace with the actual cost of opening the case
            description=f"Opening case {case_id} at {datetime.now()}"
        )

        gifts = self.get_case_gifts(case_id)
        gifts.sort(key=lambda gift: gift.prob, reverse=True)

        # Предварительно строим массив кумулятивных вероятностей
        cum_probs = []
        running = 0
        for gift in gifts:
            running += gift.prob
            cum_probs.append(running)

        r = int(random.random() * 100 * 100)
        print(r)
        idx = bisect(cum_probs, r)
        prize = gifts[idx]
        return prize
    

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