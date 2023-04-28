from asyncio import get_event_loop, sleep

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from websockets.exceptions import ConnectionClosedOK

from .ws_manager import ws_manager
from .youtube_chat import get_chat_id, get_chat_messages

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


async def chat_ws_task(chat_id: str, next_token: str | None = None):
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

    await loop.create_task(chat_ws_task(chat_id, next_token))


@app.on_event('startup')
async def start_socket():
    global loop

    chat_id = await get_chat_id()

    if not chat_id:
        raise BlockingIOError('Youtube API error to connect!')

    loop = get_event_loop()
    loop.create_task(chat_ws_task(chat_id))


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
