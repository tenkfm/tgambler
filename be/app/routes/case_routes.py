from fastapi import APIRouter, HTTPException, Header
from app.container import container
from common.models.domain.gift import Gift
from app.utils.wrappers import router_try_wrapper

case_router = APIRouter(prefix="/api/case", tags=["cases"])

@case_router.get("/")
@router_try_wrapper
async def get_active_cases():
    """
    🧾 Fetch all active cases.
    :return: A list of active cases.
    """
    cases = container.case_controller.get_active_cases()
    return {"cases": cases}
    

@case_router.get("/{case_id}/info")
@router_try_wrapper
async def get_case_info(case_id: str):
    """
    ℹ Fetch detailed information about a specific case by its ID.
    :param case_id: The ID of the case to fetch.
    :return: Detailed information about the case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    case = container.case_controller.get_case_by_id(case_id)
    return container.case_controller.get_case_info(case)
    

@case_router.get("/{case_id}/gifts")
@router_try_wrapper
async def get_case_gifts(case_id: str):
    """
    🎁 Fetch all active gifts for a specific case.
    :param case_id: The ID of the case for which to fetch gifts.
    :return: A list of active gifts associated with the specified case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    gifts = container.case_controller.get_case_gifts(case_id)
    return {"gifts": gifts}


@case_router.post("/{case_id}/gifts")
@router_try_wrapper
async def add_gift_to_case(case_id: str, gift: Gift):
    """
    ➕ Add a new gift to the specified case.
    :param case_id: The ID of the case to which the gift belongs.
    :param gift: The Gift object to be added.
    :return: The added Gift object with its ID.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    container.case_controller.add_gift(case_id, gift)
    return {"status": "ok"}
    

@case_router.post("/{case_id}/open")
@router_try_wrapper
async def open_case(case_id: str, x_token: str = Header(...)):
    """
    🚀 Open a case by its ID.
    :param case_id: The ID of the case to open.
    :return: A random gift from the opened case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    user_id = container.user_ctonroller.validate_token(x_token)    
    return container.case_controller.open_case(user_id, case_id)

    
@case_router.post("/{openning_id}/redep")
@router_try_wrapper
async def redep_openning(openning_id: str, x_token: str = Header(...)):
    """
    🔄 Redep an existing case opening - Topup balance with openning gift volume
    :param openning_id: The ID of the case opening to reuse.
    :return: A random gift from the reused case opening.
    """
    if not openning_id:
        raise HTTPException(status_code=400, detail="Openning ID is required")
    
    user_id = container.user_ctonroller.validate_token(x_token)    
    # Redep an existing case opening
    return container.case_controller.redep_openning(openning_id, user_id)

    
@case_router.post("/{openning_id}/save")
@router_try_wrapper
async def save_openning(openning_id: str, x_token: str = Header(...)):
    """
    💾 Save an existing case opening to inventory
    :param openning_id: The ID of the case opening to save.
    :return: A random gift from the saved case opening.
    """

    if not openning_id:
        raise HTTPException(status_code=400, detail="Openning ID is required")
    
    user_id = container.user_ctonroller.validate_token(x_token)
    # Save an existing case opening
    return container.case_controller.save_to_inventory(openning_id, user_id)
