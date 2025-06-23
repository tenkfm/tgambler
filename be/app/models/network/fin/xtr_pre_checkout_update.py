from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, ConfigDict
from common.models.domain.wallet import Currency


class XTRFrom(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: str
    language_code: str
    is_premium: bool

class XTRChat(BaseModel):
    id: int
    first_name: str
    username: str
    type: str

class XTRPreCheckoutUpdate(BaseModel):
    class PreCheckoutQuery(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        
        id: str
        sender: XTRFrom = Field(..., alias="from")
        currency: Currency
        total_amount: int
        invoice_payload: str
        
    model_config = ConfigDict(populate_by_name=True)

    # Fields
    update_id: int
    pre_checkout_query: PreCheckoutQuery

class XTRSuccessfulPayment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    currency: Currency
    total_amount_in_stars: int = Field(..., alias="total_amount")
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str

class XTRSuccessfulPaymentRequest(BaseModel):
    class XTRSuccessfulPaymentMessage(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        @field_validator("date", mode="before")
        @classmethod
        def _parse_unix_timestamp(cls, v):
            if isinstance(v, (int, float)):
                # приводим к UTC‐datetime
                return datetime.fromtimestamp(v, tz=timezone.utc)
            return v

        # Fields
        message_id: int
        sender: XTRFrom = Field(..., alias="from")
        chat: XTRChat
        date: datetime
        successful_payment: XTRSuccessfulPayment
        payload: Optional[str] = None

    update_id: int
    message: XTRSuccessfulPaymentMessage
