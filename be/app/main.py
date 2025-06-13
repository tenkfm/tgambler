from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from models import Payment, InvoiceRequest
import requests

import requests as req

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize any resources here if needed
    print("Starting up the application...")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/invoice")
async def invoice(request: Request):
    request_data = await request.json()
    invoice_request = InvoiceRequest(**request_data)
    
    # Create the invoice
    try:
        invoice = create_invoice(invoice_request.th_id, invoice_request.amount)
        return invoice
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# Neet to set a webhook - https://api.telegram.org/bot7785197610:AAGbHyutLPa3R0XiSdliwbfoYnQYZF15E8A/setWebhook?url=https://fuzzy-waddle-rrqjpx67xrcgjw-8000.app.github.dev/webhooks/telegram
@app.post("/webhooks/telegram")
async def telegram_webhook(request: Request):
    update = await request.json()

    if 'pre_checkout_query' in update:
        #  update= {'update_id': 101074410, 'pre_checkout_query': {'id': '1336649942687528887', 'from': {'id': 311213066, 'is_bot': False, 'first_name': 'Tony', 'username': 'call_me_anton', 'language_code': 'en', 'is_premium': True}, 'currency': 'XTR', 'total_amount': 3, 'invoice_payload': '311213066&&&e639736a-cd60-48cf-bdc3-a4d94cea9f21'}}
        print("[pre_checkout_query] received")
        id = update['pre_checkout_query']['id']
        url = f"https://api.telegram.org/bot7785197610:AAGbHyutLPa3R0XiSdliwbfoYnQYZF15E8A/answerPreCheckoutQuery"
        requests.post(url, data={"pre_checkout_query_id": id, "ok": True})
        return {"status": "success"}
    
    # Successful payment
    elif 'successful_payment' in update.get("message", {}):

        # update = {'update_id': 101074411, 'message': {'message_id': 6, 'from': {'id': 311213066, 'is_bot': False, 'first_name': 'Tony', 'username': 'call_me_anton', 'language_code': 'en', 'is_premium': True}, 'chat': {'id': 311213066, 'first_name': 'Tony', 'username': 'call_me_anton', 'type': 'private'}, 'date': 1749803575, 'successful_payment': {'currency': 'XTR', 'total_amount': 3, 'invoice_payload': '311213066&&&e639736a-cd60-48cf-bdc3-a4d94cea9f21', 'telegram_payment_charge_id': 'stxeeSrNw270fEHxc_aCu7DKCMk2D_GJ6vIqAOVc0J21rYZ9KyfIdlKMP-8uKEjGdE7XM0cIOiTjNTuCszBlDWBzExigbYrxM5gh8fsSdO2ols_4Zdh5DI6X_sqZrDdStoZ', 'provider_payment_charge_id': '311213066_8'}}}

        print("[successful_payment] received")
        order_id = update.get("message", {}).get("successful_payment", {}).get("invoice_payload")  # Get invoice payload
        print("order_id:", order_id)
        # Update your payment record based on order ID
        try:
            # Save successful payment transaction
            return {"status": "success"}
        except Exception as e:  
            print("[error, data not valid]", str(e))  
            return {"status": "fail"}

def create_invoice(th_id, amount) -> dict:
    order_id = th_id

    # Save payment in the database
    payment = Payment(
        user_id=th_id,
        amount=amount,
        order_id=order_id,
        currency="XTR",
        status="pending",
        created_at=None  # Set to current time if needed
    )

    # Set payload with payment details
    payload = f"{order_id}&&&{payment.id}"
    data = {
        "title": "Gift Mistery Box",
        "description": "Mistery Box with Unique Telegram Gifts",
        "payload": payload,
        "currency": "XTR",
        "prices": [{"label": "Telegram Stars", "amount": int(amount)}]
    }

    headers = {'Content-Type': 'application/json'}
    url = f"https://api.telegram.org/bot7785197610:AAGbHyutLPa3R0XiSdliwbfoYnQYZF15E8A/createInvoiceLink"
    response = requests.post(url, json=data, headers=headers)

    if response.ok and response.json().get('ok'):
        return {"url": response.json()['result']}
    raise Exception("Invoice creation failed.")