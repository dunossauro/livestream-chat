from asyncio import sleep

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
BASE_URL = 'https://www.googleapis.com/youtube/v3/{}'


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.websocket('/ws/chat')
async def chat(websocket: WebSocket):
    next_token = None
    chat_id = await get_chat_id()
    await ws_manager.connect(websocket)

    if not chat_id:
        await ws_manager.broadcast(
            {'type': 'error', 'name': 'Error', 'message': 'livechat.id Error!'}
        )
        logger.error('Socket Closed, error with chat_id.')
        ws_manager.disconnect(websocket)
        return {'message': 'Error'}

    try:
        while True:
            (
                time_to_next_request,
                next_token,
                chat_messages,
                has_messages
            ) = await get_chat_messages(chat_id, next_token)

            logger.debug(f'{time_to_next_request=}, {next_token=}.')

            for message in chat_messages:
                await ws_manager.broadcast(message.dict())
                await sleep(0.5)

            if not has_messages:
                logger.info('Not messages, waiting 5 seconds...')
                await sleep(5)

            if time_to_next_request > 0:
                await sleep(time_to_next_request)

    except ConnectionClosedOK:
        ws_manager.disconnect(websocket)
