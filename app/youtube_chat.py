from asyncio import AbstractEventLoop, sleep
from logging import INFO
from os import environ
from typing import AsyncGenerator

from dotenv import load_dotenv
from httpx import AsyncClient, TimeoutException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk import init
from sentry_sdk.integrations.logging import EventHandler, LoggingIntegration

from .schemas import ChatSchema
from .ws_manager import WebSocketManager

load_dotenv()
API_KEY = environ['GOOGLE_API_KEY']
youtube_live_id = environ['YOUTUBE_LIVESTREAM_ID']

BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'
mongo_client = AsyncIOMotorClient(environ['MONGO_URI'])

logger.add(
    'data/livechat_log.log',
    rotation='1 week',
    format='{time} {level} {message}',
    level='DEBUG',
)

init(
    dsn=environ['SENTRY_DSN'],
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0,
)

logger.add(
    EventHandler(level=INFO), format='{time} {level} {message}', level='INFO'
)


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
    except IndexError:
        logger.error('Youtube video ID is wrong or not found.')

    except KeyError:
        logger.error('Youtube video ID is wrong or not found.')

    return chat_id


def time_to_next_request(items: list[dict], interval: float) -> float:
    items_size = len(items)
    animation_time = items_size * 0.5
    youtube_interval = interval * 0.001
    return youtube_interval - animation_time


async def format_messages(
    messages: list[dict],
) -> AsyncGenerator[ChatSchema, None]:
    """
    Converte a o json confuso do youtube em YoutubeChatSchema.

    Persiste no database 'youtube' todas as mensagens
    """
    for message in messages:

        db = mongo_client.youtube.chat_messages
        await db.insert_one(message)

        yield ChatSchema(
            type=message['snippet']['type'],
            name=message['authorDetails']['displayName'],
            message=message['snippet']['displayMessage'],
        )


async def get_chat_messages(
    chat_id: str, next_token: str | None = None
) -> tuple[float, str | None, AsyncGenerator[ChatSchema, None], int]:
    params = {
        'part': 'snippet,authorDetails',
        'key': environ['GOOGLE_API_KEY'],
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

    try:
        total_time = time_to_next_request(
            messages['items'], messages['pollingIntervalMillis']
        )
    except Exception as exc:
        logger.error(exc)
        logger.error(messages)
        return 1, next_token, format_messages([]), 5

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
):
    if ws_manager.connections:
        (
            time_to_next_request,
            next_token,
            chat_messages,
            has_messages,
        ) = await get_chat_messages(chat_id, next_token)

        logger.debug(f'{time_to_next_request=}, {next_token=}.')

        async for message in chat_messages:
            await ws_manager.broadcast(message.dict())

        if not has_messages:
            logger.debug('Not messages, waiting 5 seconds...')
            await sleep(5)

        if time_to_next_request > 0:
            logger.debug(f'TIME TO NEXT {time_to_next_request}')
            await sleep(time_to_next_request)
        else:
            await sleep(1)
    else:
        logger.debug('WAITING SOCKETSSSSS')
        await sleep(5)

    await loop.create_task(
        chat_ws_task(chat_id, next_token, loop=loop, ws_manager=ws_manager)
    )
