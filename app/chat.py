from os import environ

from httpx import AsyncClient

API_KEY = environ['GOOGLE_API_KEY']
youtube_live_id = environ['LIVESTREAM_ID']

BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'


async def get_chat_id(video_id=youtube_live_id):
    params = {'part': 'liveStreamingDetails', 'key': API_KEY, 'id': video_id}

    url = BASE_URL.format('videos')
    async with AsyncClient() as client:
        response = await client.get(url, params=params)
        video_info = response.json()
        chat_id = video_info['items'][0]['liveStreamingDetails'][
            'activeLiveChatId'
        ]

    return chat_id


def time_to_next_request(items, interval):
    items_size = len(items)
    animation_time = items_size * 0.5
    youtube_interval = interval * 0.001
    return youtube_interval - animation_time
