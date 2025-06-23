# tests/utils/mock_fin_controller.py

class MockFinController:
    def transfer_funds_from_user_to_app(self, user_id: str, amount: int, description: str):
        return

    def transfer_funds_from_app_to_user(self, user_id: str, amount: int, description: str):
        return
