from datetime import datetime
from zoneinfo import ZoneInfo

from app.models import Comment


def test_comments_should_have_all_fields():
    comment = Comment(
        id=1,
        name='test',
        comment='test comment',
        live='live test',
        created_at=datetime.now(tz=ZoneInfo('America/Sao_Paulo')).now(),
    )

    assert comment
