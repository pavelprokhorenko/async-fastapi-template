from fastapi import APIRouter

from app.api.v1.endpoints import login, user

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login")
api_router.include_router(user.router, prefix="/user", tags=["user"])
