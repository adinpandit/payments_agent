-- 001_initial_schema.sql
-- Initial Yaadi schema: organizations, customers, ledger_entries.
-- Target: PostgreSQL 16 (gen_random_uuid() is built in since PG 13).

BEGIN;

CREATE TABLE IF NOT EXISTS organizations (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id  UUID         NOT NULL,
    name             VARCHAR(150) NOT NULL,
    phone            VARCHAR(20),
    email            VARCHAR(255),
    address          VARCHAR(500),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_customer_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations (id),

    -- Lets ledger_entries reference (organization_id, id) so an entry can
    -- never point at a customer belonging to a different organization.
    CONSTRAINT unique_organization_customer
        UNIQUE (organization_id, id)
);

-- Covered by the leading column of unique_organization_customer as well,
-- but kept explicit for the WHERE organization_id = ... ORDER BY name lookup.
CREATE INDEX IF NOT EXISTS idx_customer_organization
    ON customers (organization_id);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id  UUID          NOT NULL,
    customer_id      UUID          NOT NULL,
    entry_type       VARCHAR(30)   NOT NULL,
    direction        VARCHAR(10)   NOT NULL,
    amount           NUMERIC(12,2) NOT NULL,
    description      VARCHAR(500),
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ledger_customer
        FOREIGN KEY (organization_id, customer_id)
        REFERENCES customers (organization_id, id),

    CONSTRAINT valid_entry_type
        CHECK (
            entry_type IN (
                'sale',
                'payment',
                'opening_balance',
                'adjustment'
            )
        ),

    CONSTRAINT valid_direction
        CHECK (direction IN ('debit', 'credit')),

    CONSTRAINT positive_amount
        CHECK (amount > 0),

    CONSTRAINT valid_sale_direction
        CHECK (entry_type <> 'sale' OR direction = 'debit'),

    CONSTRAINT valid_payment_direction
        CHECK (entry_type <> 'payment' OR direction = 'credit'),

    CONSTRAINT valid_opening_balance_direction
        CHECK (entry_type <> 'opening_balance' OR direction = 'debit')
);

-- Serves the composite FK, the balance aggregate, and the per-customer
-- statement query (WHERE org/customer ORDER BY created_at DESC, id DESC).
CREATE INDEX IF NOT EXISTS idx_ledger_customer
    ON ledger_entries (organization_id, customer_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_ledger_created_at
    ON ledger_entries (created_at DESC);

COMMIT;
