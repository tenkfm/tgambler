import sys
import requests
from pathlib import Path
from app.settings import Settings
from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.wallet import Wallet
from app.container import container

sys.path.append(str(Path(__file__).resolve().parents[1]))

def application_setup():
    """
    This function sets up the application by initializing the Firebase service.
    It can be extended to include other setup tasks as needed.
    """

    try:
        if check_app_is_set_up():
            print("🛑 Don't need to set up application, it is already set up.")
            return
    
        # Create App Wallet
        create_app_wallet()

        # Setup Telegram API webhook
        setup_telegram_api_webhook()
        print("💵 Application wallet created successfully.")
    except Exception as e:
        print(f"❌ Application setup Error: {e}")
        return    

    print("✅ Application setup completed successfully.")

def check_app_is_set_up():
    """
    Check if the application is set up by verifying the existence of the app wallet.
    """
    try:
        app_wallet = container.firebase_service.fetch_by_id(doc_id=Settings().app_wallet_id, model_class=Wallet)
        if not app_wallet:
            print("Application is not set up.")
            return False
        print("Application is set up.")
        return True
    except Exception as e:
        raise Exception(f"Error checking application setup: {e}") from e

def create_app_wallet():
    wallet = Wallet(
        id=Settings().app_wallet_id,
        user_id="",
        balance=0,
        currency="TON",
    )
    container.firebase_service.add_with_doc_id(doc_id=Settings().app_wallet_id, obj=wallet)

def setup_telegram_api_webhook():
    bot_token = Settings().telegram_bot_token
    webhook_url = f"{Settings().app_domain}/webhook/telegram_xtr_invoice"

    url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception(f"Failed to set webhook: {resp.text}")
    else:
        print("✅ Webhook set successfully.")

if __name__ == "__main__":
    application_setup()