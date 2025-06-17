from fastapi import APIRouter, HTTPException, Depends
from models.domain.user import User
from services.container import container
from models.domain.case import Case

case_router = APIRouter(prefix="/api/case", tags=["cases"])

@case_router.get("/")
async def get_active_cases():
    try:
        cases = container.case_controller.get_active_cases()
        return {"cases": cases}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@case_router.get("/{case_id}/gifts")
async def get_active_cases(case_id: str):
    try:
        gifts = container.case_controller.get_gifts(case_id)
        return {"gifts": gifts}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))