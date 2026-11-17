"""Tests for strict finance request validation."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from modules.finance.domain.models import AccountCreate, TransactionRequest


def test_finance_rejects_zero_and_negative_transfer_amounts():
    for amount in ("0", "-1.00"):
        with pytest.raises(ValidationError):
            TransactionRequest(
                from_account="cash",
                to_account="bank",
                amount=amount,
            )


def test_finance_rejects_unexpected_request_fields():
    with pytest.raises(ValidationError):
        TransactionRequest(
            from_account="cash",
            to_account="bank",
            amount="10.25",
            unexpected="not allowed",
        )


def test_finance_converts_json_numbers_to_decimal_without_binary_artifacts():
    request = TransactionRequest(
        from_account="cash",
        to_account="bank",
        amount=10.25,
    )
    assert request.amount == Decimal("10.25")


def test_finance_uses_decimal_and_myanmar_currency_defaults():
    request = TransactionRequest(
        from_account="cash",
        to_account="bank",
        amount="12.50",
    )
    account = AccountCreate(
        account_id="cash",
        name="Cash in hand",
        opening_balance="100.00",
    )
    assert request.amount == Decimal("12.50")
    assert account.currency == "MMK"
