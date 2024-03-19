from asyncio import get_event_loop, sleep
from contextlib import asynccontextmanager
from os import environ
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from websockets.exceptions import ConnectionClosedOK

from .logger import logger
from .schemas import HighlightSchema, WSClient
from .twitch_bot import Bot
from .ws_manager import ws_manager
from .youtube_chat import chat_ws_task, get_chat_id

load_dotenv()


@asynccontextmanager
async def start_socket(app: FastAPI):  # noqa: ARG001
    logger.info('start app')
    loop = get_event_loop()
    services = environ['SERVICES'].split(',')

    if 'youtube' in services:
        chat_id = await get_chat_id()

        if not chat_id:
            msg = 'Youtube API error to connect!'
            raise BlockingIOError(msg)

        loop.create_task(
            chat_ws_task(chat_id, loop=loop, ws_manager=ws_manager),
        )

    if 'twitch' in services:
        loop.create_task(Bot(loop, ws_manager).start())

    yield

    logger.info('end app')


app = FastAPI(lifespan=start_socket)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/health')
def health():
    return {'status': 'OK'}


@app.post('/span', status_code=201)
async def span(data: HighlightSchema):
    await ws_manager.broadcast(
        {
            'message': data.message,
            'channel': 'messages',
            'name': data.name,
            'type': 'textMessageEvent',
        },
    )
    return {'status': 'OK'}


@app.post('/highlight', status_code=201)
async def highlight(data: HighlightSchema):
    try:
        await ws_manager.broadcast(
            {
                'message': data.message,
                'channel': 'event',
                'name': data.name,
                'type': 'textMessageEvent',
            },
        )
    except Exception as ex:  # noqa: BLE001
        logger.critical(f'Deu ex: {ex}')
    return {'status': 'OK'}


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.get('/highlight', response_class=HTMLResponse)
def highlight_view(request: Request):
    return templates.TemplateResponse('highlight.html', {'request': request})


@app.websocket('/ws/chat/{channel}')
async def chat(websocket: WebSocket, channel: Literal['messages', 'event']):
    ws: WSClient = {'web_socket': websocket, 'channel': channel}
    await ws_manager.connect(ws)

    try:
        while True:
            await sleep(10)

    except ConnectionClosedOK:
        ws_manager.disconnect(ws)
