#every future SQLAlchemy model (User, Url, ClickEvent) must inherit from one shared base class. Alembic will later read that base’s metadata to generate migrations.
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass