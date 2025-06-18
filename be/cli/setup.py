import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.settings import Settings
from app.services.firebase.firebase_service import FirebaseService
from app.models.domain.wallet import Wallet
from app.services.container import container

def application_setup():
    """
    This function sets up the application by initializing the Firebase service.
    It can be extended to include other setup tasks as needed.
    """
    
    if check_app_is_set_up():
        print("Don't need to set up application, it is already set up.")
        return

    try:
        # Create App Wallet
        create_app_wallet()
        print("Application wallet created successfully.")
    except Exception as e:
        print(f"Error creating application wallet: {e}")
        return    

    print("Application setup completed successfully.")

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
        print(f"Error checking application setup: {e}")
        return True

def create_app_wallet():
    wallet = Wallet(
        id=Settings().app_wallet_id,
        user_id="",
        balance=0,
        currency="TON",
    )
    container.firebase_service.add_with_doc_id(doc_id=Settings().app_wallet_id, obj=wallet)

if __name__ == "__main__":
    application_setup()