from fastapi import APIRouter, HTTPException, Header
from app.models.domain.user import UserInfo
from app.services.container import container

user_router = APIRouter(prefix="/api/user", tags=["users"])

@user_router.post("/launch")
async def user_launch_app(user: UserInfo):
    """
    On application launch we want to create/update user id and info in the database
    """
    try:
        return container.user_ctonroller.on_launch(user)  # Call the controller method to handle user launch
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/referral")
async def set_referral_user(ref_id: str, x_token: str = Header(...)):
    """
    Set the referral user based on the provided referral ID.
    This function can be used as a dependency in routes to set the referral user.
    """
    if not ref_id:
        raise HTTPException(status_code=400, detail="ref_id is required")
    
    try:
        user_id = container.user_ctonroller.validate_token(x_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        return container.user_ctonroller.set_referral_user(user_id=user_id, ref_id=ref_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Save referral error")
    

@user_router.get("/")
async def get_profile():
    try:
        prompt = container.prompt_controller.create_prompt(prompt)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))