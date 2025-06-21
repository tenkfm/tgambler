from fastapi import APIRouter, HTTPException, Depends, Header
from app.services.container import container
from app.models.domain.gift import Gift
from app.models.network.fin.wallet_topup_request import WalletTopupRequest
from app.models.domain.wallet import Currency
from app.models.network.fin.xtr_invoice import XTRInvoice
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
        currency=Currency.TON,  # Assuming TON is the currency used
        description=request.description,
        external_id="Manual"
    )

    return {"status": "ok"}

@fin_router.post("/xtr_invoice")
@router_try_wrapper
async def invoice(invoice: XTRInvoice, x_token: str = Header(...)):
    """
    🧾 Create an invoice for XTR top up
    :param invoice: The invoice details to be created.
    :param x_token: The user's authentication token.
    :return: The created invoice or an error message.
    """
    
    user_id = container.user_ctonroller.validate_token(x_token)
    
    # Create the invoice and return invoice url
    return container.fin_controller.send_xtr_invoice_to_telegram(user_id=user_id, title="Buy Case Stars", description="You buy stars in Case game", invoice=invoice)