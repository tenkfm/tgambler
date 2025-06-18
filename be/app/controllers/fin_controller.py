from fastapi import Depends
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter
from app.controllers.base_controller import BaseController
from app.services.firebase.firebase_service import FirebaseService
from app.models.domain.wallet import Transaction, Wallet
from app.settings import Settings

class FinController(BaseController):
    _firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService = Depends(FirebaseService)):
        self._firebase_service = firebase_service

    def topup_user_wallet(
            self,
            user_id: str,
            amount: int,
            description: str
        ):
        """
        Top up user wallet with the specified amount and description.
        :param user_id: ID of the user whose wallet is to be topped up.
        :param amount: Amount to be topped up in cents.
        :param description: Description of the top-up request.
        :raises Exception: If the user wallet is not found or if there are insufficient funds.
        """

        user_wallets = self._firebase_service.fetch_all(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", "TON")]
        )
        
        if not user_wallets:
            raise Exception("User wallet not found")
        
        from_wallet_id = Settings().app_wallet_id
        user_wallet = user_wallets[0]
        to_wallet_id = user_wallet.id

        # Update the user's wallet balance
        user_wallet.balance += amount
        self._firebase_service.update(user_wallet.id, user_wallet)

        # Create a new transaction
        transaction = Transaction(
            from_wallet_id="_TopUp",
            to_wallet_id=to_wallet_id,
            amount=amount,
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

        user_wallets = self._firebase_service.fetch_all(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", "TON")]
        )

        if not user_wallets:
            raise Exception("User wallet not found")
        
        from_wallet_id = Settings().app_wallet_id
        to_wallet_id = user_wallets[0].id  # Assuming the first wallet is the one to use

        self.__process_transaction(
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
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

        user_wallets = self._firebase_service.fetch_all(
            model_class=Wallet,
            filters=[FieldFilter("user_id", "==", user_id), FieldFilter("currency", "==", "TON")]
        )

        if not user_wallets:
            raise Exception("User wallet not found")
        
        from_wallet_id = user_wallets[0].id
        to_wallet_id = Settings().app_wallet_id

        self.__process_transaction(
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            amount=amount,
            description=description
        )

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