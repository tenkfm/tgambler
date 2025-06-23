from fastapi import APIRouter, HTTPException, Request
from app.container import container
from app.utils.wrappers import router_try_wrapper
from app.models.network.fin.xtr_pre_checkout_update import XTRPreCheckoutUpdate, XTRSuccessfulPaymentRequest
from common.models.domain.wallet import TopUpRequest, TopUpStatus, Currency
from common.models.domain.user import UserInfo
from google.cloud.firestore_v1.base_query import FieldFilter
from app.settings import Settings
import requests

webhook_router = APIRouter(prefix="/webhook", tags=["webhooks"])

@webhook_router.post("/telegram_xtr_invoice")
@router_try_wrapper
async def telegram_invoice_webhook(request: Request):
    raw = await request.json()
    # Payment pre checkout
    if 'pre_checkout_query' in raw:
        payload = XTRPreCheckoutUpdate.model_validate(raw)
        return __telegram_invoice_pre_checkout_query(payload)
        
     # Successful payment
    elif 'successful_payment' in raw.get("message", {}):
        payload = XTRSuccessfulPaymentRequest.model_validate(raw)
        return __telegram_invoice_successful_payment(payload=payload)


#
# Private methods
#

def __telegram_invoice_pre_checkout_query(checkout: XTRPreCheckoutUpdate):
    """
    Handle the pre-checkout query for Telegram invoice.
    This function is called when a user initiates a payment.
    """

    print("Received pre-checkout query webhook from Telegram")

    external_id = checkout.pre_checkout_query.invoice_payload

    topup_request = container.firebase_service.fetch_one(TopUpRequest, filters=[FieldFilter("external_id", "==", external_id)])

    if not topup_request:
        __answerPreCheckoutQuery(data={"pre_checkout_query_id": checkout.pre_checkout_query.id, "error_message": "Top-up request not found", "ok": False})
        raise HTTPException(status_code=400, detail="Top-up request not found")

    if topup_request.status != TopUpStatus.PENDING:
        __answerPreCheckoutQuery(data={"pre_checkout_query_id": checkout.pre_checkout_query.id, "error_message": "Top-up request is not in pending status", "ok": False})
        raise HTTPException(status_code=400, detail="Top-up request is not in pending status")
    
    response = __answerPreCheckoutQuery(data={"pre_checkout_query_id": checkout.pre_checkout_query.id, "ok": True})

    # Successful result
    if response.ok and response.json().get('ok') == True:
        topup_request.status = TopUpStatus.PROCESSING
        container.firebase_service.update(id=topup_request.id, obj=topup_request)
        return {"status": "success"}
    
    # Failed result
    topup_request.status = TopUpStatus.FAILED
    topup_request.info = response.json().get('description', 'Unknown error')
    container.firebase_service.update(id=topup_request.id, obj=topup_request)
    raise HTTPException("Pre-checkout query failed.")


def __answerPreCheckoutQuery(data: dict):
    """
    Answer the pre-checkout query for Telegram invoice.
    This function sends a response to Telegram indicating whether the pre-checkout query was successful.
    """
    url = f"https://api.telegram.org/bot{Settings().telegram_bot_token}/answerPreCheckoutQuery"
    response = requests.post(url, data=data)
    return response


def __telegram_invoice_successful_payment(payload: XTRSuccessfulPaymentRequest):
    """
    Handle the successful payment for Telegram invoice.
    This function is called when a user completes a payment.
    """

    print("Received successful payment webhook from Telegram")

    th_id = payload.message.sender.id
    if not th_id:
        raise HTTPException(status_code=400, detail="Telegram user ID is missing in the payload")
    
    user = container.firebase_service.fetch_one(
        UserInfo,
        filters=[FieldFilter("tg_id", "==", th_id)]
    )

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    external_id = payload.message.successful_payment.invoice_payload

    # Top up user's wallet
    container.fin_controller.topup_user_wallet(
        user_id=user.id,
        amount=payload.message.successful_payment.total_amount_in_stars * 100,
        currency=Currency.XTR,
        description=f"Top-up from Telegram Stars (ID: {payload.message.successful_payment.telegram_payment_charge_id})",
        external_id=external_id
    )

    # Change topup_request status to success
    topup_request = container.firebase_service.fetch_one(
        TopUpRequest,
        filters=[FieldFilter("external_id", "==", external_id)]
    )

    if not topup_request:
        raise HTTPException(status_code=400, detail="Top-up request not found")

    topup_request.status = TopUpStatus.SUCCESS
    topup_request.info = payload.model_dump()
    container.firebase_service.update(id=topup_request.id, obj=topup_request)
    return {"status": "success"}