BEGIN;

-- Prevent modification of existing ledger entries.
CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION
        'Ledger entries cannot be updated or deleted. Create a correcting adjustment instead.';
END;
$$;

-- Remove existing triggers if this migration is reapplied.
DROP TRIGGER IF EXISTS prevent_ledger_update
ON ledger_entries;

DROP TRIGGER IF EXISTS prevent_ledger_delete
ON ledger_entries;

-- Prevent UPDATE operations.
CREATE TRIGGER prevent_ledger_update
BEFORE UPDATE ON ledger_entries
FOR EACH ROW
EXECUTE FUNCTION prevent_ledger_mutation();

-- Prevent DELETE operations.
CREATE TRIGGER prevent_ledger_delete
BEFORE DELETE ON ledger_entries
FOR EACH ROW
EXECUTE FUNCTION prevent_ledger_mutation();

COMMIT;