from fastapi import APIRouter, HTTPException, Depends, Header
from app.services.container import container
from app.models.domain.gift import Gift
from app.services.container import container
from app.models.network.fin.wallet_topup_request import WalletTopupRequest
from app.utils.wrappers import router_try_wrapper

fin_router = APIRouter(prefix="/api/fin", tags=["finances"])

@fin_router.post("/topup")
@router_try_wrapper
async def topup_user_wallet(request: WalletTopupRequest, x_token: str = Header(...)):
    """
    💰 Top up user wallet.
    :return: A message indicating the top-up was successful.
    """
    user_id = container.user_ctonroller.validate_token(x_token)

    container.fin_controller.topup_user_wallet(
        user_id=user_id,
        amount=request.amount,  # Example amount, replace with actual logic
        description=request.description
    )

    return {"status": "ok"}
