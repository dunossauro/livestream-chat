from os import environ

from dotenv import load_dotenv
from httpx import AsyncClient, TimeoutException
from loguru import logger
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
API_KEY = environ['GOOGLE_API_KEY']
MONGO_URI = environ['MONGO_URI']
youtube_live_id = environ['LIVESTREAM_ID']
BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'
logger.error(environ['LIVESTREAM_ID'])
logger.error(environ['MONGO_URI'])
mongo_client = AsyncIOMotorClient(MONGO_URI)


class YoutubeChatSchema(BaseModel):
    type: str
    name: str
    message: str


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


async def format_messages(messages: list[dict]):
    """
    Converte a o json confuso do youtube em YoutubeChatSchema.

    Persiste no database 'youtube' todas as mensagens
    """
    for message in messages:

        db = mongo_client.youtube.chat_messages
        await db.insert_one(message)

        yield YoutubeChatSchema(
            type=message['snippet']['type'],
            name=message['authorDetails']['displayName'],
            message=message['snippet']['displayMessage'],
        )


async def get_chat_messages(chat_id: str, next_token: str | None = None):
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
            logger.info('TimeoutException, wait 1 second...')
            return 1, next_token, [], 0

    total_time = time_to_next_request(
        messages['items'], messages['pollingIntervalMillis']
    )

    messages_to_socket = format_messages(messages.get('items'))

    return total_time, messages.get('nextPageToken'), messages_to_socket, len(messages.get('items'))
