from fastapi import APIRouter
from .auth import router as AuthRouter
from .user import router as UserRouter
from .content import router as ContentRouter

routers = APIRouter()
routers.include_router(AuthRouter)
routers.include_router(UserRouter)
routers.include_router(ContentRouter)