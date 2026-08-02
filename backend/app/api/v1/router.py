from fastapi import APIRouter
from app.api.v1.endpoints.urls import router as urls_router
from app.api.v1.endpoints.auth import router as auth_router

router=APIRouter()
router.include_router(urls_router)
router.include_router(auth_router)