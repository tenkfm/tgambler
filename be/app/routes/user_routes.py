from fastapi import APIRouter, HTTPException, Header
from app.models.domain.user import UserInfo
from app.services.container import container
from app.utils.wrappers import router_try_wrapper

user_router = APIRouter(prefix="/api/user", tags=["users"])

@user_router.post("/launch")
@router_try_wrapper
async def user_launch_app(user: UserInfo):
    """
    On application launch we want to create/update user id and info in the database
    """
    return container.user_ctonroller.on_launch(user)  # Call the controller method to handle user launch


@user_router.post("/referral")
@router_try_wrapper
async def set_referral_user(ref_id: str, x_token: str = Header(...)):
    """
    Set the referral user based on the provided referral ID.
    This function can be used as a dependency in routes to set the referral user.
    """
    if not ref_id:
        raise HTTPException(status_code=400, detail="ref_id is required")
    
    user_id = container.user_ctonroller.validate_token(x_token)
    return container.user_ctonroller.set_referral_user(user_id=user_id, ref_id=ref_id)
    

@user_router.get("/")
@router_try_wrapper
async def get_profile():
    return {"status": "ok"}
