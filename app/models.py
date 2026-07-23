from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserAuditMixin:
    created_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('users.id'),
        init=False,
        default=None,
    )

    updated_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('users.id'),
        init=False,
        default=None,
    )


class AuditMixin(TimestampMixin, UserAuditMixin):
    pass


table_registry = registry()


@mapped_as_dataclass(table_registry)
class User(AuditMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
