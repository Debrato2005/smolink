from fastapi import APIRouter
from app.api.v1.endpoints.urls import router as urls_router

router=APIRouter()
router.include_router(urls_router)