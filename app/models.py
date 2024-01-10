from datetime import datetime
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    comment: Mapped[str]
    live: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now
    )

    def __repr__(self):
        return f'Comment({self.id=}, {self.name=}, {self.comment=}, {self.live=}, {self.created_at=})'  # NOQA
