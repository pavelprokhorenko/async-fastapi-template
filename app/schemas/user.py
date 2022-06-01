from pydantic import EmailStr

from app.schemas import BaseSchema


class BaseUser(BaseSchema):
    email: EmailStr
    phone_number: str | None
    is_active: bool | None = True
    is_superuser: bool | None = False


class UserIn(BaseUser):
    password: str
    first_name: str
    last_name: str


class UserUpdate(BaseUser):
    email: EmailStr | None
    password: str | None
    first_name: str | None
    last_name: str | None


class User(BaseUser):
    id: int
    first_name: str
    last_name: str
