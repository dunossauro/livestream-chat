from asyncio import get_event_loop
from contextlib import asynccontextmanager
from os import environ

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles


from .containers import Container
from .logger import logger
from .routes import app as app_router
from .ws_manager import WebSocketManager
from .twitch_bot import Bot
from .youtube_chat import chat_ws_task, get_chat_id

load_dotenv()


@asynccontextmanager
@inject
async def start_socket(
    app: FastAPI, # noqa: ARG001
    ws_manager: WebSocketManager = Depends(Provide[Container.ws_manager]),
):
    logger.info('start app')
    loop = get_event_loop()
    services = environ['SERVICES'].split(',')

    if 'youtube' in services:
        chat_id = await get_chat_id()

        if not chat_id:
            msg = 'Youtube API error to connect!'
            raise BlockingIOError(msg)

        loop.create_task(  # noqa: RUF006
            chat_ws_task(chat_id, loop=loop, ws_manager=ws_manager),
        )

    if 'twitch' in services:
        loop.create_task(Bot(loop, ws_manager).start())  # noqa: RUF006

    yield

    logger.info('end app')

app = FastAPI(lifespan=start_socket)
app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(app_router)
container = Container()
app.container = container
