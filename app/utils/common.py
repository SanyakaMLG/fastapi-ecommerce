from fastapi_users import FastAPIUsers
from app.models import User
from app.services.manager import get_user_manager
from app.services.auth import auth_backend


fastapi_users= FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


current_user = fastapi_users.current_user


def remap_available_filters(mapping):
    return [{'key': k, 'value': list(v)} for k, v in mapping.items()]