from psycopg.rows import dict_row
from app.db.connection import get_pool

def create_organization(name:str)->dict:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO organizations (name)
                VALUES (%s)
                RETURNING id , name ,created_at
                """,
                (name,),
            )

            organization = cur.fetchone()

    return organization

def get_organization(organization_id)->dict | None:
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, name, created_at
                FROM organizations
                WHERE id = %s
                """,
                (organization_id,),
            )

            return cur.fetchone()