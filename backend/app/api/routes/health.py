from fastapi import APIRouter, HTTPException
from app.db.connection import check_database_connection

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("/")
def health_check():

    return {
        "status": "healthy",
        "service": "yaadi-api",
    }

@router.get("/db")
def database_health_check():

    is_connected = check_database_connection()

    if not is_connected:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )

    return {
        "status": "healthy",
        "database": "connected",
    }