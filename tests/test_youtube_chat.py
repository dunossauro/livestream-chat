import pytest
from httpx import Response, TimeoutException
from respx import MockRouter

from app.models import YTChatToken
from app.youtube_chat import format_messages, get_chat_messages, get_chat_id

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
    interval, token, _, number_of_messages = await get_chat_messages('1234')

    assert interval == expected_interval / 1_000
    assert token == expected_token
    assert number_of_messages == 0


@pytest.mark.asyncio()
async def test_get_chat_messages_should_receive_timeout_exception(
    respx_mock: MockRouter,
):
    respx_mock.get(youtube_api_url).mock(side_effect=TimeoutException)

    interval, *_, number_of_messages = await get_chat_messages('1234')

    assert interval == 1
    assert number_of_messages == 0


@pytest.mark.asyncio()
async def test_get_chat_messages_should_receive_keyerror_exception(
    respx_mock: MockRouter,
):
    respx_mock.get(youtube_api_url).mock(
        return_value=Response(200, json={}),
    )

    interval, *_, number_of_messages = await get_chat_messages('1234')

    assert interval == 1
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


@pytest.mark.asyncio()
async def test_get_chat_id(respx_mock: MockRouter, mocker, session, token):
    mock_response = {
        'items': [
            {'liveStreamingDetails': {'activeLiveChatId': 'live_token'}}
        ],
    }

    mock = respx_mock.get('https://www.googleapis.com/youtube/v3/videos').mock(
        return_value=Response(200, json=mock_response)
    )

    patch = mocker.patch('app.youtube_chat.async_session')
    patch.return_value = session

    result = await get_chat_id('live_id')
    assert result.live_token == 'live_token'

    token_db = await session.get(YTChatToken, 'live_id')
    assert token_db.live_token == 'live_token'


@pytest.mark.asyncio()
async def test_get_chat_id_not_found_token_indexerror(
    respx_mock: MockRouter, caplog
):
    mock_response = {'items': []}

    mock = respx_mock.get('https://www.googleapis.com/youtube/v3/videos').mock(
        return_value=Response(200, json=mock_response)
    )

    result = await get_chat_id()
    assert not result
    assert (
        caplog.record_tuples[0][2] == 'Youtube video ID is wrong or not found.'
    )
    assert str(mock_response) in caplog.record_tuples[1][2]


@pytest.mark.asyncio()
async def test_get_chat_id_not_found_token_keyerror(
    respx_mock: MockRouter, caplog
):
    mock_response = {}

    mock = respx_mock.get('https://www.googleapis.com/youtube/v3/videos').mock(
        return_value=Response(200, json=mock_response)
    )

    result = await get_chat_id()
    assert not result
    assert (
        caplog.record_tuples[0][2] == 'Youtube video ID is wrong or not found.'
    )
    assert str(mock_response) in caplog.record_tuples[1][2]
