# Models inherit from this shared base to register one metadata collection.
# Alembic imports app.models before using Base.metadata for autogeneration.

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
