from typing import Optional

from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserCreate
from app.services.auth import get_user_db
from app.config import SECRET

secret = SECRET


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = secret
    verification_token_secret = secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def create(
            self, user_create: schemas.UC, safe: bool = False, request=None
    ) -> User:
        existing_phone = await self.user_db.get_user_by_phone(user_create.phone)
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone already registered")
        return await super().create(user_create, safe, request)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)