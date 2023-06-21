from unittest import TestCase
from app.youtube_chat import time_to_next_request


class TestTimeToNextRequest(TestCase):
    def test_no_messages(self):
        messages = []
        time = 5
        result = time_to_next_request(messages, time)
        assert result == 5.5

    def test_with_messages(self):
        messages = [{}] * 5
        time = 5
        result = time_to_next_request(messages, time)
        assert result == 3
