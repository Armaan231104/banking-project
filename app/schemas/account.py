from pydantic import BaseModel


class AccountCreate(BaseModel):
    currency: str = 'USD'


class AccountOut(BaseModel):
    account_id: str
    balance: float
    currency: str


class StatementExportResponse(BaseModel):
    download_url: str
