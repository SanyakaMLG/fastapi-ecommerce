from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from app.models import User
from app.database import get_session
from app.config import SECRET


cookie_transport = CookieTransport(cookie_name="token", cookie_max_age=604800)
secret = SECRET


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=604800)


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

