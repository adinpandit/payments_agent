CREATE TABLE if NOT EXISTS organizations(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    created_at TIMESTAMPZ NOT NULL DEFAULT NOW(),
);

CREATE TABLE is NOT EXISTS customers(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organizations_id UUID NOT NULL,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address VARCHAR(500) NOT NULL,
    created_at TIMESTAMPZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_customer_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id),

    CONSTRAINT unique_organization_customer
        UNIQUE(organization_id,id)
);

CREATE INDEX if NOT EXISTS idx_customer_organization
on customers(organization_id)

CREATE TABLE if NOT EXISTS ledger_entries(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    entry_type VARCHAR(30) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMPZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ledger_customer
        FOREIGN KEY (organization_id,customer_id)
        REFERENCES customers(organization_id,id)

    CONSTRAINT valid_entry_type
        check(
            entry_type IN(
                'sale',
                'payment',
                'opening_balance',
                'adjustment'
            )
        ),

    CONSTRAINT valid_direction
        CHECK (irection IN ('debit','credit')),

    CONSTRAINT positive_amount
        CHECK (amount > 0),

    CONSTRAINT valid_sale_direction
        CHECK(
            entry_type != 'sale'
            OR direction = 'debit'
        ),

    CONSTRAINT valid_payment_direction
        CHECK (
            entry_type != 'payment'
            OR direction = 'credit'
        ),

    CONSTRAINT valid_opening_balance_direction
        CHECK (
            entry_type != 'opening_balance'
            OR direction = 'debit'
        )

);

CREATE INDEX if NOT EXISTS idx_ledger_customer
ON ledger_entries(organization_id,customer_id);

CREATE INDEX if NOT EXISTS idx_ledger_created_at
ON ledger_entries(created_at DESC);