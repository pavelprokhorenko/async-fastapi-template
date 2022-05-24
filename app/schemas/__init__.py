# flake8: noqa
from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


from .message import Message
from .token import Token, TokenPayload
from .user import User, UserIn, UserUpdate
