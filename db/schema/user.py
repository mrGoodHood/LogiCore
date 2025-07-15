from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from ..engine import Base


class User(SQLAlchemyBaseUserTableUUID):
    pass


class BaseUser(User, Base):
    pass