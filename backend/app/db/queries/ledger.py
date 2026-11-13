from psycopg.rows import dict_row
from app.db.connection import get_pool

def create_ledger_entry(
        organization_id,
        customer_id,
        entry_type:str,
        direction:str,
        amount,
        description:str|None,
)->dict:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO ledger_entries (
                    organization_id,
                    customer_id,
                    entry_type,
                    direction,
                    amount,
                    description
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    organization_id,
                    customer_id,
                    entry_type,
                    direction,
                    amount,
                    description,
                    created_at
                """,
                (
                    organization_id,
                    customer_id,
                    entry_type,
                    direction,
                    amount,
                    description,
                ),
            )

            return cur.fetchone()

def get_customer_entries(
    organization_id,
    customer_id,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM ledger_entries
                WHERE organization_id = %s
                  AND customer_id = %s
                """,
                (
                    organization_id,
                    customer_id,
                ),
            )
            total = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT
                    id,
                    customer_id,
                    entry_type,
                    direction,
                    amount,
                    description,
                    created_at
                FROM ledger_entries
                WHERE organization_id = %s
                  AND customer_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                OFFSET %s
                """,
                (organization_id, customer_id, limit, offset),
            )

            items = cur.fetchall()

            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

def get_customer_balance(
    organization_id,
    customer_id,
) -> dict | None:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    c.id AS customer_id,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN l.direction = 'debit'
                                THEN l.amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_debit,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN l.direction = 'credit'
                                THEN l.amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_credit,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN l.direction = 'debit'
                                THEN l.amount
                                ELSE -l.amount
                            END
                        ),
                        0
                    ) AS outstanding_balance

                FROM customers c

                LEFT JOIN ledger_entries l
                    ON l.customer_id = c.id
                    AND l.organization_id = c.organization_id

                WHERE c.organization_id = %s
                  AND c.id = %s

                GROUP BY c.id
                """,
                (organization_id, customer_id),
            )

            return cur.fetchone()