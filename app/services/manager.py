from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.models import User
from app.services.auth import get_user_db
from app.config import SECRET

secret = SECRET


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = secret
    verification_token_secret = secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)