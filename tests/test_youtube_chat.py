import pytest
from httpx import Response, TimeoutException
from respx import MockRouter

from app.youtube_chat import format_messages, get_chat_messages

youtube_api_url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'


@pytest.mark.asyncio()
async def test_format_messages_should_return_chat_schema():
    youtube_messages = [
        {
            'snippet': {
                'type': 'textMessageEvent',
                'displayMessage': 'test message',
            },
            'authorDetails': {'displayName': 'Test User'},
        },
    ]

    result = [val async for val in format_messages(youtube_messages)]
    assert result == [
        {
            'type': 'textMessageEvent',
            'name': 'Test User',
            'message': 'test message',
            'channel': 'messages',
        },
    ]


@pytest.mark.asyncio()
async def test_get_chat_messages_should_return_interval_and_token(
    respx_mock: MockRouter,
):
    expected_interval = 10
    expected_token = 'test-token'
    respx_mock.get(youtube_api_url).mock(
        return_value=Response(
            200,
            json={
                'items': [],
                'pollingIntervalMillis': expected_interval,
                'nextPageToken': expected_token,
            },
        ),
    )
    inteval, token, _, number_of_messages = await get_chat_messages('1234')

    assert inteval == expected_interval / 1_000
    assert token == expected_token
    assert number_of_messages == 0


@pytest.mark.asyncio()
async def test_get_chat_messages_should_receve_timeout_exception(
    respx_mock: MockRouter,
):
    respx_mock.get(youtube_api_url).mock(side_effect=TimeoutException)

    inteval, *_, number_of_messages = await get_chat_messages('1234')

    assert inteval == 1
    assert number_of_messages == 0


@pytest.mark.asyncio()
async def test_get_chat_messages_should_receve_keyerror_exception(
    respx_mock: MockRouter,
):
    respx_mock.get(youtube_api_url).mock(
        return_value=Response(200, json={}),
    )

    inteval, *_, number_of_messages = await get_chat_messages('1234')

    assert inteval == 1
    assert number_of_messages == 0


@pytest.mark.asyncio()
async def test_get_chat_messages_should_call_api_with_pagination_token(
    respx_mock: MockRouter,
):
    next_token = 'next-token'
    mock = respx_mock.get(youtube_api_url).mock(
        return_value=Response(200, json={}),
    )

    await get_chat_messages('1234', next_token=next_token)

    call_params = mock.calls.last.request.url.params
    assert call_params['pageToken'] == next_token
