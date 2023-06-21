from unittest import TestCase
from app.schemas import ChatSchema


class TestTimeToNextRequest(TestCase):
    def test_schema_default_type_value(self):
        schema = ChatSchema(name='Test User', message='Test Message')
        assert schema.type == 'textMessageEvent'
