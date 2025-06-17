from fastapi import APIRouter, HTTPException, Depends
from models.domain.user import User
from services.container import container
from models.domain.user import UserInfo


user_router = APIRouter(prefix="/api/user", tags=["users"])

@user_router.post("/launch")
### On application launch we want to create/update user id and info in the database
async def user_launch_app(user: UserInfo):
    try:
        return container.user_ctonroller.on_launch(user)  # Call the controller method to handle user launch
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get("/")
async def get_profile():
    try:
        prompt = container.prompt_controller.create_prompt(prompt)
        return {"prompt": prompt}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))