from os import environ

from dotenv import load_dotenv
from twitchio.ext import commands

from .schemas import ChatSchema

load_dotenv()


class Bot(commands.Bot):
    def __init__(self, loop, ws):
        self.loop = loop
        self.ws_manager = ws

        super().__init__(
            token=environ['TWITCH_TOKEN'],
            prefix='!',
            initial_channels=['dunossauro'],
        )

    async def event_message(self, message):
        message = ChatSchema(name=message.author.name, message=message.content)

        await self.ws_manager.broadcast(message.dict())
