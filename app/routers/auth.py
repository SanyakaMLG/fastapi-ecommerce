from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from app.models import User
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.auth import auth_backend
from app.services.manager import get_user_manager

fastapi_users_auth = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

router.include_router(
    fastapi_users_auth.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users_auth.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users_auth.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)