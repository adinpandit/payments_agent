from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.config import settings
from app.api.routes import health
from app.db.connection import open_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(
    title = settings.APP_NAME,
    description="Agentic AI Receivables Management Platform",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/",tags=["Root"])
def root():
    return{
        "status":"running",
        "message":"Welcome to Yaadi API",
        "application":settings.APP_NAME,
        "enviroment":settings.APP_ENV,
        "version":"0.1.0",
    }

app.include_router(health.router)