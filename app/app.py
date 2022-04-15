from asyncio import sleep
from os import environ

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient
from websockets.exceptions import ConnectionClosedOK

from .chat import get_chat_id, time_to_next_request
from .ws_manager import ws_manager

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.websocket('/ws/chat')
async def chat(websocket: WebSocket):
    await ws_manager.connect(websocket)
    chat_id = await get_chat_id()

    params = {
        'part': 'snippet,authorDetails',
        'key': environ['GOOGLE_API_KEY'],
        'liveChatId': chat_id,
        'maxResults': 200,
    }

    url = BASE_URL.format('liveChat/messages')

    try:
        while True:
            async with AsyncClient() as client:
                response = await client.get(url, params=params)
                messages = response.json()

                if messages['nextPageToken']:
                    params['pageToken'] = messages['nextPageToken']

                if not messages['items']:
                    await sleep(5)

                for item in messages['items']:
                    await sleep(0.5)
                    await ws_manager.broadcast(
                        {
                            'type': item['snippet']['type'],
                            'name': item['authorDetails']['displayName'],
                            'message': item['snippet']['displayMessage'],
                        }
                    )

                if (
                    total_time := time_to_next_request(
                        messages['items'], messages['pollingIntervalMillis']
                    )
                ) > 0:
                    await sleep(total_time)

    except ConnectionClosedOK:
        ws_manager.disconnect(websocket)
