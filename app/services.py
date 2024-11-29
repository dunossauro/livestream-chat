from asyncio import BaseEventLoop
from .twitch_bot import Bot
from .youtube_chat import chat_ws_task, get_chat_id


class Service:
    def __init__(self, ws_manager, loop: BaseEventLoop):
        self.ws_manager = ws_manager
        self.loop = loop

    async def start(self):
        ...


class Youtube(Service):
    async def start(self):
        chat_id = await get_chat_id()

        if not chat_id:
            msg = 'Youtube API error to connect!'
            raise BlockingIOError(msg)

        self.loop.create_task(  # noqa: RUF006
            chat_ws_task(chat_id, loop=self.loop, ws_manager=self.ws_manager),
        )


class Twitch(Service):
    async def start(self):
        self.loop.create_task(  # noqa: RUF006
            Bot(self.loop, self.ws_manager).start()
        )
