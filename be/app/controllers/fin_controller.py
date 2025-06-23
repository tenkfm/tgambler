import uuid
from fastapi import Depends
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter
from app.controllers.base_controller import BaseController
from app.models.network.fin.xtr_invoice import XTRInvoice
from app.settings import Settings
from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.wallet import Transaction, Wallet, TopUpRequest, Currency, TopUpStatus
import requests

class FinController(BaseController):
    _firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService = Depends(FirebaseService)):
        self._firebase_service = firebase_service

    def topup_user_wallet(
            self,
            user_id: str,
            amount: int,
            currency: Currency,
            description: str,
            external_id: str
        ):
        """
        Top up user wallet with the specified amount and description.
        :param user_id: ID of the user whose wallet is to be topped up.
        :param amount: Amount to be topped up in cents.
        :param currency: Currency of the top-up, e.g., Currency.TON.
        :param description: Description of the top-up request.
        :param external_id: External ID for the top-up request, used for tracking.
        :raises Exception: If the user wallet is not found or if there are insufficient funds.
        """

        user_wallet = self._firebase_service.fetch_one(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", currency.value)]
        )
        to_wallet_id = user_wallet.id
        
        if not user_wallet:
            raise Exception(f"User wallet not found user_id: {user_id}, currency: {currency.value}")

        # Update the user's wallet balance
        user_wallet.balance += amount
        self._firebase_service.update(user_wallet.id, user_wallet)

        # Create a new transaction
        transaction = Transaction(
            from_wallet_id=f"_TopUp - {external_id}",
            to_wallet_id=to_wallet_id,
            amount=amount,
            currency=currency,
            description=description,
            timestamp=datetime.now()
        )
        self._firebase_service.add(transaction)


    def transfer_funds_from_app_to_user(
            self,
            user_id: str,
            amount: int,
            description: str
        ):
        """
        Transfer funds from the app's wallet to a user's wallet.
        :param user_id: The ID of the user to whom funds will be transferred.
        :param amount: The amount to transfer.
        :param description: A description for the transaction.
        :raises Exception: If the user's wallet is not found or if there are insufficient funds.
        """

        #TODO: Consider transaction currency
        to_wallet = self._firebase_service.fetch_one(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", "TON")]
        )

        if not to_wallet:
            raise Exception("User wallet not found")

        self.__process_transaction(
            from_wallet_id=Settings().app_wallet_id,
            to_wallet_id=to_wallet.id,
            amount=amount,
            description=description
        )

    def transfer_funds_from_user_to_app(
            self,
            user_id: str,
            amount: int,
            description: str
        ):
        """
        Transfer funds from a user's wallet to the app's wallet.
        :param user_id: The ID of the user from whom funds will be transferred.
        :param amount: The amount to transfer.
        :param description: A description for the transaction.
        :raises Exception: If the user's wallet is not found or if there are insufficient funds.
        """

        #TODO: Consider transaction currency
        user_wallet = self._firebase_service.fetch_one(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", "TON")]
        )

        if not user_wallet:
            raise Exception("User wallet not found")
        
        from_wallet_id = user_wallet.id
        to_wallet_id = Settings().app_wallet_id

        self.__process_transaction(
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            amount=amount,
            description=description
        )


    def send_xtr_invoice_to_telegram(self, user_id: str, title: str, description: str, invoice: XTRInvoice) -> dict:
        """
        Create an invoice for a user to pay in XTR (Telegram Stars).
        :param invoice: An instance of XTRInvoice containing the details.
        :return: A dictionary containing the invoice URL.
        :raises Exception: If the invoice creation fails.
        """

        # Save XTRTopUp in the database
        external_id = f"{invoice.th_id}&&&{uuid.uuid4()}"
        topup_request = TopUpRequest(
            user_id=user_id,
            amount=invoice.amount,
            provider="Telegram",
            currency=Currency.XTR,
            external_id=external_id,
            status=TopUpStatus.PENDING,
            created_at=datetime.now()
        )
        topup_request = self._firebase_service.add(topup_request)

        # Set payload with payment details
        data = {
            "title": title,
            "description": description,
            "payload": external_id,
            "currency": "XTR",
            "prices": [{"label": "Telegram Stars", "amount": int(invoice.amount / 100)}]
        }

        # Send request to Telegram API to create invoice link
        headers = {'Content-Type': 'application/json'}
        url = f"https://api.telegram.org/bot{Settings().telegram_bot_token}/createInvoiceLink"
        response = requests.post(url, json=data, headers=headers)

        # Successful result
        if response.ok and response.json().get('ok'):
            topup_request.info = {"url": response.json()['result']}
            self._firebase_service.update(id=topup_request.id, obj=topup_request)
            return {"url": response.json()['result']}
        
        # Failed result
        topup_request.status = TopUpStatus.FAILED
        topup_request.info = response.json()
        self._firebase_service.update(id=topup_request.id, obj=topup_request)
        raise Exception("Invoice creation failed.")


    #
    # Private methods
    #

    def __process_transaction(
            self,
            from_wallet_id: str,
            to_wallet_id: str,
            amount: int,
            description: str
        ):
        """
        Process a transaction between two wallets.
        :param from_wallet_id: The ID of the wallet from which funds will be deducted.
        :param to_wallet_id: The ID of the wallet to which funds will be added.
        :param amount: The amount to transfer.
        :param description: A description for the transaction.
        :raises Exception: If either wallet is not found or if there are insufficient funds.
        """

        print(from_wallet_id)
        print(to_wallet_id)
        
        from_wallet = self._firebase_service.fetch_by_id(
            model_class=Wallet,
            doc_id=from_wallet_id
        )

        to_wallet = self._firebase_service.fetch_by_id(
            model_class=Wallet,
            doc_id=to_wallet_id
        )

        if not from_wallet or not to_wallet:
            raise Exception("Wallets not found")
        if from_wallet.balance < amount:
            raise Exception(f"Insufficient balance in the sender wallet. Need: {amount/100:.2f}, Available: {from_wallet.balance/100:.2f}")
        
        # Create a new transaction
        transaction = Transaction(
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            amount=amount,
            currency=Currency.TON,  # Transactions are in TON currency
            description=description,
            timestamp=datetime.now()
        )
        
        # Deduct amount from sender's wallet
        from_wallet.balance -= transaction.amount
        # Add amount to receiver's wallet
        to_wallet.balance += transaction.amount
        # Update the wallets in the database
        self._firebase_service.update(id=from_wallet.id, obj=from_wallet)
        self._firebase_service.update(id=to_wallet.id, obj=to_wallet)
        
        # Save the transaction
        return self._firebase_service.add(transaction)
