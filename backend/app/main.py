from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import health
from app.db.connection import open_pool, close_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()

app = FastAPI(
    title="Yaadi API",
    description="Agentic AI-powered receivables management platform",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/")
def root():

    return {
        "message": "Welcome to Yaadi API",
        "status": "running",
    }

app.include_router(health.router)