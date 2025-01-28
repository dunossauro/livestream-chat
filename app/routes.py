from typing import Literal
from asyncio import sleep

from fastapi import APIRouter, Depends, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import Provide, inject
from websockets.exceptions import ConnectionClosedOK

from .containers import Container
from .ws_manager import WebSocketManager
from .schemas import HighlightSchema, WSClient
from .logger import logger

app = APIRouter()
templates = Jinja2Templates(directory='templates')


@app.get('/health')
def health():
    return {'status': 'OK'}


@app.post('/highlight', status_code=201)
@inject
async def highlight(
    data: HighlightSchema,
    ws_manager: WebSocketManager = Depends(Provide[Container.ws_manager]),
):
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
    return templates.TemplateResponse(request, 'chat.html')


@app.get('/highlight', response_class=HTMLResponse)
def highlight_view(request: Request):
    return templates.TemplateResponse(request, 'highlight.html')


@app.websocket('/ws/chat/{channel}')
@inject
async def chat(
    websocket: WebSocket,
    channel: Literal['messages', 'event'],
    ws_manager: WebSocketManager = Depends(Provide[Container.ws_manager]),
):
    ws: WSClient = {'web_socket': websocket, 'channel': channel}
    await ws_manager.connect(ws)

    try:
        while True:
            await sleep(10)

    except ConnectionClosedOK:
        logger.info(f'{channel} desconectado.')
        ws_manager.disconnect(ws)
