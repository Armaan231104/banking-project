from pydantic import BaseModel, Field


class DepositRequest(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    currency: str
    idempotency_key: str | None = None
    description: str | None = None


class WithdrawRequest(DepositRequest):
    pass


class TransferRequest(BaseModel):
    source_account_id: str
    destination_account_id: str
    amount: float = Field(gt=0)
    currency: str
    idempotency_key: str | None = None
    description: str | None = None


class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    currency: str
    flagged_fraud: bool
