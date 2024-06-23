from asyncio import AbstractEventLoop, sleep
from os import environ
from typing import AsyncGenerator

from dotenv import load_dotenv
from emoji import emojize
from httpx import AsyncClient, ConnectError, TimeoutException

from .database import async_session
from .logger import logger
from .models import Comment
from .ws_manager import WebSocketManager, WSMessage

load_dotenv()
API_KEY = environ['GOOGLE_API_KEY']
youtube_live_id = environ['YOUTUBE_LIVESTREAM_ID']
use_db = True

BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'


async def get_chat_id(video_id: str = youtube_live_id) -> str:
    params = {'part': 'liveStreamingDetails', 'key': API_KEY, 'id': video_id}
    chat_id = ''

    url = BASE_URL.format('videos')

    async with AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        video_info = response.json()

    try:
        chat_id = video_info['items'][0]['liveStreamingDetails'][
            'activeLiveChatId'
        ]
    except IndexError as e:
        logger.error('Youtube video ID is wrong or not found.')
        logger.debug(f'{video_info} - {e}')

    except KeyError as e:
        logger.error('Youtube video ID is wrong or not found.')
        logger.debug(f'{video_info} - {e}')

    return chat_id


async def format_messages(
    messages: list[dict],
) -> AsyncGenerator[WSMessage, None]:
    """Converte a o json confuso do youtube em YoutubeChatSchema."""
    for message in messages:
        yield {
            'type': message['snippet']['type'],
            'name': message['authorDetails']['displayName'],
            'message': emojize(message['snippet']['displayMessage']),
            'channel': 'messages',
        }
        comment = Comment(
            name=message['authorDetails']['displayName'],
            comment=message['snippet']['displayMessage'],
            live='youtube',
        )
        if use_db:
            async with async_session() as session:
                session.add(comment)
                await session.commit()
        else:
            logger.debug(comment)


async def get_chat_messages(
    chat_id: str,
    next_token: str | None = None,
) -> tuple[float, str | None, AsyncGenerator[WSMessage, None], int]:
    params = {
        'part': 'snippet,authorDetails',
        'key': API_KEY,
        'liveChatId': chat_id,
        'maxResults': 200,
    }

    if next_token:
        params['pageToken'] = next_token

    url = BASE_URL.format('liveChat/messages')

    async with AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            messages = response.json()
        except TimeoutException as exc:
            logger.error(exc)
            logger.debug('TimeoutException, wait 1 second...')
            return 1, next_token, format_messages([]), 0
        except ConnectError as exc:
            logger.error(exc)
            logger.debug('ConnectError: f{url}, wait 2 second...')
            return 2, next_token, format_messages([]), 0

    try:
        total_time = messages['pollingIntervalMillis'] / 1_000
    except Exception as exc:  # noqa: BLE001
        logger.error(exc)
        logger.error(messages)
        return 1, next_token, format_messages([]), 0

    messages_to_socket = format_messages(messages.get('items'))

    return (
        total_time,
        messages.get('nextPageToken'),
        messages_to_socket,
        len(messages.get('items')),
    )


async def chat_ws_task(
    chat_id: str,
    next_token: str | None = None,
    *,
    loop: AbstractEventLoop,
    ws_manager: WebSocketManager,
) -> None:
    if ws_manager.connections:
        (
            time_to_next_request,
            next_token,
            chat_messages,
            has_messages,
        ) = await get_chat_messages(chat_id, next_token)

        logger.debug(f'{time_to_next_request=}, {next_token=}.')

        async for message in chat_messages:
            await ws_manager.broadcast(message)
            await sleep(0.5)

        if not has_messages:
            logger.debug('Not messages, waiting 15 seconds...')
            await sleep(15)

        if time_to_next_request > 0:
            logger.debug(f'TIME TO NEXT {time_to_next_request}')
            time = time_to_next_request + (has_messages * 0.5)
            logger.debug(f'Waiting {time}')
            await sleep(time)
        else:
            await sleep(1)
    else:
        logger.debug('WAITING SOCKETSSSSS')
        await sleep(5)

    await loop.create_task(
        chat_ws_task(chat_id, next_token, loop=loop, ws_manager=ws_manager),
    )
