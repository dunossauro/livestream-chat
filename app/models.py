from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Comment:
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    comment: Mapped[str]
    live: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        init=False,
        default=datetime.now,
    )


@table_registry.mapped_as_dataclass
class YTChatToken:
    __tablename__ = 'ytchattoken'

    live_id: Mapped[str] = mapped_column(primary_key=True)
    token: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        init=False,
        default=datetime.now,
    )
