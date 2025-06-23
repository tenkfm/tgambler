from pydantic import BaseModel

class WalletTopupRequest(BaseModel):
    amount: int  # Amount to be topped up in cents
    description: str  # Description of the top-up request