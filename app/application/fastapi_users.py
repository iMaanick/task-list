from fastapi_users import FastAPIUsers

from app.application.auth_backend import auth_backend
from app.application.user_manager import get_user_manager

from app.adapters.sqlalchemy_db.models import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
