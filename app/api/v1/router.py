from fastapi import APIRouter

from app.api.v1.endpoints import login

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login")
