import logging
import psycopg
from psycopg_pool import PoolTimeout
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(psycopg.IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: psycopg.IntegrityError,
    ):

        logger.warning(
            "Database integrity error on %s: %s",
            request.url.path,
            type(exc).__name__,
        )

        return JSONResponse(
            status_code=409,
            content={
                "error": "database_integrity_error",
                "message": "The operation conflicts with existing database constraints.",
            },
        )

    @app.exception_handler(PoolTimeout)
    async def pool_timeout_handler(
        request: Request,
        exc: PoolTimeout,
    ):

        logger.error(
            "Database connection pool timeout on %s",
            request.url.path,
        )

        return JSONResponse(
            status_code=503,
            content={
                "error": "database_unavailable",
                "message": "Database is temporarily unavailable. Please try again.",
            },
        )

    @app.exception_handler(psycopg.OperationalError)
    async def operational_error_handler(
        request: Request,
        exc: psycopg.OperationalError,
    ):

        logger.error(
            "Database operational error on %s: %s",
            request.url.path,
            type(exc).__name__,
        )

        return JSONResponse(
            status_code=503,
            content={
                "error": "database_unavailable",
                "message": "Database is temporarily unavailable. Please try again.",
            },
        )

    @app.exception_handler(psycopg.Error)
    async def database_error_handler(
        request: Request,
        exc: psycopg.Error,
    ):

        logger.exception(
            "Unexpected database error on %s",
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "database_error",
                "message": "A database error occurred.",
            },
        )
