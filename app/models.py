from __future__ import annotations

from datetime import datetime
from typing import Optional, Self

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    name: Mapped[str]
    comment: Mapped[str]
    live: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        default=datetime.now,
    )

    def __repr__(self: Self) -> str:
        return f'Comment({self.id=}, {self.name=}, {self.comment=}, {self.live=}, {self.created_at=})'  # noqa: E501
