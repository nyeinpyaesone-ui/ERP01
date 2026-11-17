"""Strict request and response models for ledger-safe finance operations."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


AccountId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
]
CurrencyCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{3}$", min_length=3, max_length=3),
]
PositiveAmount = Annotated[
    Decimal,
    Field(gt=Decimal("0"), max_digits=20, decimal_places=2),
]


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: AccountId
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    currency: CurrencyCode = "MMK"
    opening_balance: Annotated[
        Decimal,
        Field(ge=Decimal("0"), max_digits=20, decimal_places=2),
    ] = Decimal("0.00")


class AccountBalanceResponse(BaseModel):
    account_id: str
    balance: Decimal
    currency: str
    updated_at: datetime


class TransactionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_account: AccountId
    to_account: AccountId
    amount: PositiveAmount
    description: Annotated[str | None, Field(max_length=500)] = None
    reference: Annotated[str | None, Field(max_length=120)] = None


class TransactionResponse(BaseModel):
    transaction_id: str
    from_account: str
    to_account: str
    amount: Decimal
    currency: str
    description: str | None
    reference: str | None
    idempotency_key: str
    created_at: datetime
    replayed: bool = False


class AccountResponse(BaseModel):
    account_id: str
    name: str
    currency: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
