from pydantic import EmailStr

from app.schemas import BaseSchema


class BaseUser(BaseSchema):
    email: EmailStr
    phone_number: str | None
    first_name: str | None
    last_name: str | None
    is_active: bool | None = True
    is_superuser: bool | None = False


class UserIn(BaseUser):
    password: str


class UserUpdate(UserIn):
    email: EmailStr | None
    password: str | None


class User(BaseUser):
    id: int
