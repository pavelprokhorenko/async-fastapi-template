from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    id: int = Column(Integer, primary_key=True, auto_created=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(127), nullable=False)
    phone_number: str = Column(String(63))
    first_name: str = Column(String(63))
    last_name: str = Column(String(63))
    is_active: bool = Column(Boolean, server_default=True)
    is_superuser: bool = Column(Boolean, server_default=True)
