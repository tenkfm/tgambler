from pydantic import BaseModel

class XTRInvoice(BaseModel):
    th_id: int
    amount: int