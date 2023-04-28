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


@app.on_event("startup")
async def connect_youtube():
    global chat_id
    chat_id = await get_chat_id()

    if not chat_id:
        logger.error('Youtube API error to connect!')


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.websocket('/ws/chat')
async def chat(websocket: WebSocket):
    """
    Funciona, mas agora duplica as mensagens.
    """
    next_token = None
    await ws_manager.connect(websocket)

    try:
        while True:
            # Esse bloco tem que ser executado fora do socket!
            (
                time_to_next_request,
                next_token,
                chat_messages,
                has_messages,
            ) = await get_chat_messages(chat_id, next_token)

            logger.debug(f'{time_to_next_request=}, {next_token=}.')

            # Até aqui!

            async for message in chat_messages:
                await ws_manager.broadcast(message.dict())
                await sleep(0.5)

            # Esses dois blocos também tem que sair daqui
            if not has_messages:
                logger.debug('Not messages, waiting 5 seconds...')
                await sleep(5)

            if time_to_next_request > 0:
                await sleep(time_to_next_request)
            # Até aqui!

    except ConnectionClosedOK:
        ws_manager.disconnect(websocket)
