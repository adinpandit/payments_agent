from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import (
    health,
    organization,
    customers,
    ledger,
)
from app.db.connection import open_pool, close_pool
from app.core.exceptions import register_exception_handlers



@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    try:
        yield
    finally:
        close_pool()

app = FastAPI(
    title="Yaadi API",
    description=
    """
    Agentic AI-powered receivables management platform.

    Current capabilities:
    - Organization management
    - Customer management
    - Ledger entries
    - Customer balance calculation
    - Paginated customer and ledger APIs
    """,
    version="0.2.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

@app.get("/")
def root():

    return {
        "message": "Welcome to Yaadi API",
        "status": "running",
    }

app.include_router(health.router)
app.include_router(organization.router)
app.include_router(customers.router)
app.include_router(ledger.router)