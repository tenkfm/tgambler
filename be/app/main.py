from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError
from app.settings import Settings
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user_routes import user_router
from app.routes.case_routes import case_router
from app.routes.fin_routes import fin_router
from app.routes.webhook_routes import webhook_router
from app.models.network.fin.xtr_pre_checkout_update import XTRPreCheckoutUpdate

###
### Load global params
###
@lru_cache()
def get_settings():
    return Settings()

###
### Initialize any resources here if needed
###
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    yield

###
### FastAPI application setup
### Middleware setup
### Routes setup
###
app = FastAPI(lifespan=lifespan)
settings = get_settings()
app.include_router(user_router)
app.include_router(case_router)
app.include_router(fin_router)
app.include_router(webhook_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

###
### Endpoints
###
@app.get("/")
async def root():
    """
    Root endpoint to check if the server is running.
    """

    return {"message": f"Roll the case and get your gifts on @{settings.bot_username}"}