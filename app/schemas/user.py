from typing import Optional

from pydantic import EmailStr

from app.schemas import BaseSchema


class BaseUser(BaseSchema):
    email: EmailStr
    phone_number: Optional[str] = ""
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserIn(BaseUser):
    password: str
    first_name: str
    last_name: str


class UserUpdate(BaseUser):
    email: Optional[EmailStr]
    password: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class User(BaseUser):
    id: int
    first_name: str
    last_name: str
