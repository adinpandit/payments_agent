
import os
import uuid
from contextlib import contextmanager

import psycopg
import pytest

from app.db import connection as connection_module
from app.db.connection import (
    open_pool,
    close_pool,
    get_pool,
    build_connection_string,
)
from app.db.queries import organizations, customers, ledger


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Set RUN_DB_INTEGRATION=1 to run PostgreSQL integration tests",
)


@pytest.fixture(scope="module", autouse=True)
def database_pool():
    open_pool()

    try:
        # Fail loudly (not skip) if the schema the tests rely on is missing.
        with get_pool().connection() as conn:
            has_ledger_table, has_immutability_trigger = conn.execute(
                """
                SELECT
                    to_regclass('public.ledger_entries') IS NOT NULL,
                    EXISTS (
                        SELECT 1
                        FROM pg_trigger
                        WHERE tgrelid = to_regclass('public.ledger_entries')
                          AND tgname IN ('prevent_ledger_update', 'prevent_ledger_delete')
                        HAVING COUNT(*) = 2
                    )
                """
            ).fetchone()

        if not has_ledger_table:
            pytest.fail("Migration 001_initial_schema.sql has not been applied")
        if not has_immutability_trigger:
            pytest.fail("Migration 002_ledger_immutability.sql has not been applied")

        yield
    finally:
        close_pool()


class _SingleConnectionPool:
    """
    Stand-in for the pool that hands every query the same connection.

    Each `connection()` block runs inside a SAVEPOINT of one outer
    transaction, so the real query functions run unchanged against
    PostgreSQL while nothing they write is ever committed.
    """

    def __init__(self, conn):
        self._conn = conn

    @contextmanager
    def connection(self):
        with self._conn.transaction():
            yield self._conn


@contextmanager
def rolled_back_transaction():
    """
    Route every `get_pool().connection()` call to one connection inside a
    single transaction that is always rolled back, even if the body raises.

    The query modules call `get_pool()` at call time, and `get_pool()` reads
    the `app.db.connection.pool` global, so swapping that global is enough
    to make the unchanged production queries share this transaction.
    """

    real_pool = get_pool()

    with real_pool.connection() as conn:
        with conn.transaction(force_rollback=True):
            connection_module.pool = _SingleConnectionPool(conn)
            try:
                yield
            finally:
                connection_module.pool = real_pool


@pytest.fixture(autouse=True)
def isolated_transaction(request, database_pool):
    """
    Roll back everything a test writes. Ledger rows cannot be deleted
    (immutability trigger), so committed test data would be permanent.

    Tests that request `manual_transaction` manage the rollback themselves.
    """

    if "manual_transaction" in request.fixturenames:
        yield
        return

    with rolled_back_transaction():
        yield


@pytest.fixture
def manual_transaction():
    """Opt out of the automatic per-test transaction."""


COUNT_ORGANIZATION_ROWS_SQL = """
    SELECT
        (SELECT COUNT(*) FROM organizations WHERE id = %(org)s),
        (SELECT COUNT(*) FROM customers WHERE organization_id = %(org)s),
        (SELECT COUNT(*) FROM ledger_entries WHERE organization_id = %(org)s)
"""


def count_rows_for_organization(organization_id):
    """
    Count rows for an organization over a brand-new connection that is not
    from the pool, so it only sees committed data.
    """

    with psycopg.connect(build_connection_string()) as conn:
        return conn.execute(
            COUNT_ORGANIZATION_ROWS_SQL,
            {"org": organization_id},
        ).fetchone()


def create_test_customer():

    organization = organizations.create_organization(
        name=f"Integration Test {uuid.uuid4().hex[:8]}"
    )

    customer = customers.create_customer(
        organization_id=organization["id"],
        name="Integration Customer",
        phone=None,
        email=None,
        address=None,
    )

    return organization, customer


def test_postgres_ledger_workflow():

    organization, customer = create_test_customer()

    organization_id = organization["id"]
    customer_id = customer["id"]

    ledger.create_ledger_entry(
        organization_id=organization_id,
        customer_id=customer_id,
        entry_type="sale",
        direction="debit",
        amount="7000.00",
        description="Integration test sale",
    )

    ledger.create_ledger_entry(
        organization_id=organization_id,
        customer_id=customer_id,
        entry_type="payment",
        direction="credit",
        amount="3000.00",
        description="Integration test payment",
    )

    balance = ledger.get_customer_balance(
        organization_id=organization_id,
        customer_id=customer_id,
    )

    assert balance is not None
    assert balance["total_debit"] == 7000
    assert balance["total_credit"] == 3000
    assert balance["outstanding_balance"] == 4000


def test_ledger_entries_are_immutable():

    organization, customer = create_test_customer()

    entry = ledger.create_ledger_entry(
        organization_id=organization["id"],
        customer_id=customer["id"],
        entry_type="sale",
        direction="debit",
        amount="1000.00",
        description="Immutable test entry",
    )

    # The trigger uses RAISE EXCEPTION (SQLSTATE P0001); any other error
    # (e.g. a missing table) must not count as "immutable".
    with pytest.raises(
        psycopg.errors.RaiseException,
        match="Ledger entries cannot be updated or deleted",
    ):
        with get_pool().connection() as conn:
            conn.execute(
                """
                UPDATE ledger_entries
                SET description = %s
                WHERE id = %s
                """,
                (
                    "Attempted modification",
                    entry["id"],
                ),
            )

    # The failed UPDATE must not have changed the original record.
    with get_pool().connection() as conn:
        result = conn.execute(
            """
            SELECT description
            FROM ledger_entries
            WHERE id = %s
            """,
            (entry["id"],),
        ).fetchone()

    assert result[0] == "Immutable test entry"


def test_ledger_entries_are_immutable_on_delete():

    organization, customer = create_test_customer()

    entry = ledger.create_ledger_entry(
        organization_id=organization["id"],
        customer_id=customer["id"],
        entry_type="sale",
        direction="debit",
        amount="1000.00",
        description="Immutable delete test entry",
    )

    with pytest.raises(
        psycopg.errors.RaiseException,
        match="Ledger entries cannot be updated or deleted",
    ):
        with get_pool().connection() as conn:
            conn.execute(
                "DELETE FROM ledger_entries WHERE id = %s",
                (entry["id"],),
            )

    # The failed DELETE must not have removed the record.
    with get_pool().connection() as conn:
        result = conn.execute(
            """
            SELECT id, amount, description
            FROM ledger_entries
            WHERE id = %s
            """,
            (entry["id"],),
        ).fetchone()

    assert result is not None
    assert result[0] == entry["id"]
    assert result[1] == entry["amount"]
    assert result[2] == "Immutable delete test entry"


def test_rolled_back_transaction_leaves_no_records(manual_transaction):

    with rolled_back_transaction():
        organization, customer = create_test_customer()
        organization_id = organization["id"]

        ledger.create_ledger_entry(
            organization_id=organization_id,
            customer_id=customer["id"],
            entry_type="sale",
            direction="debit",
            amount="500.00",
            description="Rollback probe entry",
        )

        # Visible inside the test transaction, through the real queries.
        assert organizations.get_organization(organization_id) is not None
        assert customers.get_customer(organization_id, customer["id"]) is not None
        assert ledger.get_customer_entries(organization_id, customer["id"])["total"] == 1

        # The same count query does see the rows inside the transaction,
        # so the (0, 0, 0) checks below cannot pass because of a bad query.
        with get_pool().connection() as conn:
            assert conn.execute(
                COUNT_ORGANIZATION_ROWS_SQL,
                {"org": organization_id},
            ).fetchone() == (1, 1, 1)

        # Not committed: an independent connection cannot see it yet.
        assert count_rows_for_organization(organization_id) == (0, 0, 0)

    assert get_pool() is not None and not isinstance(get_pool(), _SingleConnectionPool)

    # After rollback, an independent connection finds nothing for this org.
    assert count_rows_for_organization(organization_id) == (0, 0, 0)


def test_rolled_back_transaction_rolls_back_when_test_fails(manual_transaction):

    class SimulatedTestFailure(Exception):
        pass

    organization_id = None

    with pytest.raises(SimulatedTestFailure):
        with rolled_back_transaction():
            organization, _ = create_test_customer()
            organization_id = organization["id"]
            raise SimulatedTestFailure

    assert organization_id is not None
    assert count_rows_for_organization(organization_id) == (0, 0, 0)
