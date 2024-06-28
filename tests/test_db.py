from datetime import datetime

from zoneinfo import ZoneInfo

from app.models import Comment


def test_comments_should_have_all_fields():
    comment = Comment(
        name='test',
        comment='test comment',
        live='live test',
    )

    assert comment
