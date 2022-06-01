import sqlalchemy
import sqlalchemy_utils

from app.db.metadata import postgres_metadata

user = sqlalchemy.Table(
    "user",
    postgres_metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column(
        "email", sqlalchemy_utils.EmailType, unique=True, index=True, nullable=False
    ),
    sqlalchemy.Column("hashed_password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("phone_number", sqlalchemy.String),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("is_superuser", sqlalchemy.Boolean, default=False),
)
