from typing import Optional, Annotated, AsyncGenerator

from fastapi import Request, Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.adapters.sqlalchemy_db.models import User
from app.api.depends_stub import Stub

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        print(f"User {user.id} has registered.")


async def get_user_manager(
        user_db: Annotated[SQLAlchemyUserDatabase,
                           Depends(Stub(SQLAlchemyUserDatabase))]
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
