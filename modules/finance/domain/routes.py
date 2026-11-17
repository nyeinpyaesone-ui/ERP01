"""Finance API: staff-only accounts and idempotent, atomic account transfers."""

from decimal import Decimal
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from .models import (
    AccountBalanceResponse,
    AccountCreate,
    AccountResponse,
    TransactionRequest,
    TransactionResponse,
)
from .security import require_staff

router = APIRouter(tags=["finance"])


def _transaction_response(row, replayed: bool = False) -> TransactionResponse:
    return TransactionResponse(
        transaction_id=str(row["transaction_id"]),
        from_account=row["from_account"],
        to_account=row["to_account"],
        amount=row["amount"],
        currency=row["currency"].strip(),
        description=row["description"],
        reference=row["reference"],
        idempotency_key=row["idempotency_key"],
        created_at=row["created_at"],
        replayed=replayed,
    )


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    payload: AccountCreate,
    request: Request,
    _staff=Depends(require_staff),
):
    try:
        row = await request.app.state.db.fetchrow(
            """
            INSERT INTO finance_accounts (account_id, name, currency, balance)
            VALUES ($1, $2, $3, $4)
            RETURNING account_id, name, currency, balance, is_active, created_at, updated_at
            """,
            payload.account_id,
            payload.name,
            payload.currency,
            payload.opening_balance,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Account ID already exists.") from None

    return AccountResponse(**dict(row))



@router.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _staff=Depends(require_staff),
):
    rows = await request.app.state.db.fetch(
        """
        SELECT account_id, name, currency, balance, is_active, created_at, updated_at
        FROM finance_accounts
        ORDER BY account_id
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset,
    )
    return [AccountResponse(**dict(row)) for row in rows]


@router.get(
    "/balance/{account_id}",
    response_model=AccountBalanceResponse,
)
async def get_balance(
    account_id: str,
    request: Request,
    _staff=Depends(require_staff),
):
    row = await request.app.state.db.fetchrow(
        """
        SELECT account_id, balance, currency, updated_at
        FROM finance_accounts
        WHERE account_id = $1 AND is_active = TRUE
        """,
        account_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Active account not found.")

    return AccountBalanceResponse(
        account_id=row["account_id"],
        balance=row["balance"],
        currency=row["currency"].strip(),
        updated_at=row["updated_at"],
    )


@router.post("/transaction", response_model=TransactionResponse)
async def create_transaction(
    payload: TransactionRequest,
    request: Request,
    idempotency_key: str = Header(
        min_length=8,
        max_length=128,
        alias="Idempotency-Key",
    ),
    _staff=Depends(require_staff),
):
    if payload.from_account == payload.to_account:
        raise HTTPException(
            status_code=422,
            detail="Source and destination accounts must be different.",
        )

    pool = request.app.state.db
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Serialize requests with the same client idempotency key before
            # looking up or writing the journal row. Hash collisions only
            # serialize unrelated requests; they cannot corrupt their results.
            await conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext($1))",
                idempotency_key,
            )
            previous = await conn.fetchrow(
                """
                SELECT transaction_id, from_account, to_account, amount, currency,
                       description, reference, idempotency_key, created_at
                FROM finance_transactions
                WHERE idempotency_key = $1
                """,
                idempotency_key,
            )
            if previous:
                same_request = (
                    previous["from_account"] == payload.from_account
                    and previous["to_account"] == payload.to_account
                    and previous["amount"] == payload.amount
                    and previous["description"] == payload.description
                    and previous["reference"] == payload.reference
                )
                if not same_request:
                    raise HTTPException(
                        status_code=409,
                        detail="Idempotency key was already used for a different request.",
                    )
                return _transaction_response(previous, replayed=True)

            account_ids = sorted([payload.from_account, payload.to_account])
            rows = await conn.fetch(
                """
                SELECT account_id, currency, balance, is_active
                FROM finance_accounts
                WHERE account_id = ANY($1::varchar[])
                ORDER BY account_id
                FOR UPDATE
                """,
                account_ids,
            )
            accounts = {row["account_id"]: row for row in rows}
            source = accounts.get(payload.from_account)
            destination = accounts.get(payload.to_account)

            if source is None or destination is None:
                raise HTTPException(status_code=404, detail="Source or destination account not found.")
            if not source["is_active"] or not destination["is_active"]:
                raise HTTPException(status_code=409, detail="Both accounts must be active.")
            if source["currency"] != destination["currency"]:
                raise HTTPException(
                    status_code=409,
                    detail="Transfers between different currencies are not supported.",
                )
            if source["balance"] < payload.amount:
                raise HTTPException(status_code=409, detail="Insufficient account balance.")

            await conn.execute(
                """
                UPDATE finance_accounts
                SET balance = balance - $1, updated_at = NOW()
                WHERE account_id = $2
                """,
                payload.amount,
                payload.from_account,
            )
            await conn.execute(
                """
                UPDATE finance_accounts
                SET balance = balance + $1, updated_at = NOW()
                WHERE account_id = $2
                """,
                payload.amount,
                payload.to_account,
            )
            row = await conn.fetchrow(
                """
                INSERT INTO finance_transactions (
                    from_account, to_account, amount, currency,
                    description, reference, idempotency_key
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING transaction_id, from_account, to_account, amount, currency,
                          description, reference, idempotency_key, created_at
                """,
                payload.from_account,
                payload.to_account,
                payload.amount,
                source["currency"],
                payload.description,
                payload.reference,
                idempotency_key,
            )

    return _transaction_response(row)


@router.get("/transactions/{account_id}", response_model=list[TransactionResponse])
async def get_transactions(
    account_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    _staff=Depends(require_staff),
):
    rows = await request.app.state.db.fetch(
        """
        SELECT transaction_id, from_account, to_account, amount, currency,
               description, reference, idempotency_key, created_at
        FROM finance_transactions
        WHERE from_account = $1 OR to_account = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        account_id,
        limit,
    )
    return [_transaction_response(row) for row in rows]
