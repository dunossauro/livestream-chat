from asyncio import get_event_loop, sleep
from os import environ

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from websockets.exceptions import ConnectionClosedOK

from .twitch_bot import Bot
from .ws_manager import ws_manager
from .youtube_chat import chat_ws_task, get_chat_id

load_dotenv()
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.on_event('startup')
async def start_socket():
    loop = get_event_loop()

    services = environ['SERVICES'].split(',')

    if 'youtube' in services:
        chat_id = await get_chat_id()

        if not chat_id:
            raise BlockingIOError('Youtube API error to connect!')

        loop.create_task(
            chat_ws_task(chat_id, loop=loop, ws_manager=ws_manager)
        )

    if 'twitch' in services:
        loop.create_task(Bot(loop, ws_manager).start())


@app.get('/health')
def health():
    return {'status': 'OK'}


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.websocket('/ws/chat')
async def chat(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        while True:
            await sleep(10)

    except ConnectionClosedOK:
        ws_manager.disconnect(websocket)
