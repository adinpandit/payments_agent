from psycopg.rows import dict_row
from app.db.connection import get_pool

def create_customer(
        organization_id,
        name:str,
        phone:str|None,
        email:str|None,
        address:str|None,
)->dict:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO customers(
                    organization_id,
                    name,
                    phone,
                    email,
                    address,
                )
                VALUES (%s,%s,%s,%s,%s)
                RETURNING
                    id,
                    organization_id,
                    name,
                    phone,
                    email,
                    address,
                    created_at
                """,
                (
                    organization_id,
                    name,
                    phone,
                    email,
                    address,
                ),
            )

            return cur.fetchone()

def get_customers(organization_id)->list[dict]:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT 
                    id,
                    organization_id,
                    name,
                    phone,
                    email,
                    address,
                    created_at
                FROM customers 
                WHERE organization_id=%s
                ORDER BY name ASC
                """,
                (organization_id,),
            )

            return cur.fetchall()

def get_customer(organization_id , customer_id)->dict | None:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    id,
                    organization_id,
                    name,
                    phone,
                    email,
                    address,
                    created_at
                FROM customers
                WHERE organization_id = %s
                  AND id = %s
                """,
                (organization_id, customer_id),
            )

            return cur.fetchone()