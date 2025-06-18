from fastapi import APIRouter, HTTPException, Depends, Header
from app.services.container import container
from app.models.domain.gift import Gift

case_router = APIRouter(prefix="/api/case", tags=["cases"])


@case_router.get("/")
async def get_active_cases():
    """
    🧾 Fetch all active cases.
    :return: A list of active cases.
    """
    try:
        cases = container.case_controller.get_active_cases()
        return {"cases": cases}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@case_router.get("/{case_id}/info")
async def get_case_info(case_id: str):
    """
    ℹ Fetch detailed information about a specific case by its ID.
    :param case_id: The ID of the case to fetch.
    :return: Detailed information about the case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    try:
        case = container.case_controller.get_case_by_id(case_id)
        return container.case_controller.get_case_info(case)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@case_router.get("/{case_id}/gifts")
async def get_case_gifts(case_id: str):
    """
    🎁 Fetch all active gifts for a specific case.
    :param case_id: The ID of the case for which to fetch gifts.
    :return: A list of active gifts associated with the specified case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    try:
        gifts = container.case_controller.get_case_gifts(case_id)
        return {"gifts": gifts}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@case_router.post("/{case_id}/gifts")
async def add_gift_to_case(case_id: str, gift: Gift):
    """
    ➕ Add a new gift to the specified case.
    :param case_id: The ID of the case to which the gift belongs.
    :param gift: The Gift object to be added.
    :return: The added Gift object with its ID.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    try:
        container.case_controller.add_gift(case_id, gift)
        return {"status": "ok"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@case_router.post("/{case_id}/open")
async def open_case(case_id: str, x_token: str = Header(...)):
    """
    🚀 Open a case by its ID.
    :param case_id: The ID of the case to open.
    :return: A random gift from the opened case.
    """
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    try:
        user_id = container.user_ctonroller.validate_token(x_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        return container.case_controller.open_case(user_id, case_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@case_router.post("/{openning_id}/redep")
async def redep_openning(openning_id: str, x_token: str = Header(...)):
    """
    🔄 Redep an existing case opening - Topup balance with openning gift volume
    :param openning_id: The ID of the case opening to reuse.
    :return: A random gift from the reused case opening.
    """
    if not openning_id:
        raise HTTPException(status_code=400, detail="Openning ID is required")
    
    try:
        user_id = container.user_ctonroller.validate_token(x_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Redep an existing case opening
    try:
        return container.case_controller.redep_openning(openning_id, user_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))