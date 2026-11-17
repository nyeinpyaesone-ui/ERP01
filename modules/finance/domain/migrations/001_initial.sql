CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS finance_accounts (
    account_id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'MMK',
    balance NUMERIC(20, 2) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT finance_accounts_balance_nonnegative CHECK (balance >= 0)
);

CREATE TABLE IF NOT EXISTS finance_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_account VARCHAR(80) NOT NULL REFERENCES finance_accounts(account_id) ON DELETE RESTRICT,
    to_account VARCHAR(80) NOT NULL REFERENCES finance_accounts(account_id) ON DELETE RESTRICT,
    amount NUMERIC(20, 2) NOT NULL,
    currency CHAR(3) NOT NULL,
    description VARCHAR(500),
    reference VARCHAR(120),
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT finance_transactions_amount_positive CHECK (amount > 0),
    CONSTRAINT finance_transactions_distinct_accounts CHECK (from_account <> to_account)
);

CREATE INDEX IF NOT EXISTS finance_transactions_from_created_idx
    ON finance_transactions (from_account, created_at DESC);
CREATE INDEX IF NOT EXISTS finance_transactions_to_created_idx
    ON finance_transactions (to_account, created_at DESC);
