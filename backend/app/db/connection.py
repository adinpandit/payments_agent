import logging

import psycopg
from psycopg_pool import ConnectionPool, PoolTimeout

from app.config import settings


logger = logging.getLogger(__name__)

pool: ConnectionPool | None = None


def build_connection_string() -> str:
    """
    Build a PostgreSQL connection string safely.

    Settings.database_url uses make_conninfo, which handles special characters in passwords.
    """

    return settings.database_url


def open_pool() -> None:
    """
    Initialize the shared PostgreSQL connection pool.
    """

    global pool

    if pool is not None:
        return

    pool = ConnectionPool(
        conninfo=build_connection_string(),
        min_size=1,
        max_size=5,
        open=False,
    )

    pool.open(wait=True)

    logger.info("PostgreSQL connection pool started")


def close_pool() -> None:
    """
    Close all database connections when the application shuts down.
    """

    global pool

    if pool is not None:
        pool.close()
        pool = None

        logger.info("PostgreSQL connection pool closed")


def get_pool() -> ConnectionPool:
    """
    Return the active connection pool.
    """

    if pool is None:
        raise RuntimeError("Database connection pool is not initialized")

    return pool


def check_database_connection() -> bool:
    """
    Check whether PostgreSQL is accepting queries.
    """

    try:
        with get_pool().connection() as connection:
            connection.execute("SELECT 1").fetchone()

        return True

    except (psycopg.Error, PoolTimeout) as error:
        logger.warning(
            "Database health check failed: %s",
            type(error).__name__,
        )

        return False