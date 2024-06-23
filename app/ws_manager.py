from typing import Literal, Self, TypedDict

from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from .logger import logger
from .schemas import TypeMessages, WSClient


class WSMessage(TypedDict):
    name: str
    type: TypeMessages
    message: str
    channel: Literal['messages', 'event']


class WebSocketManager:
    def __init__(self: Self) -> None:
        self.connections: list[WSClient] = []

    async def connect(self: Self, websocket: WSClient) -> None:
        await websocket['web_socket'].accept()
        self.connections.append(websocket)

    def disconnect(self: Self, websocket: WSClient) -> None:
        self.connections.remove(websocket)

    async def broadcast(self: Self, message: WSMessage) -> None:
        for con in self.connections:
            if message['channel'] == con['channel']:
                try:
                    await con['web_socket'].send_json(message)
                except ConnectionClosedOK:
                    logger.info(f'Desconectando: {con}')
                    self.disconnect(con)
                except WebSocketDisconnect:
                    logger.info(f'Desconectando: {con}')
                    self.disconnect(con)
                except Exception as e:  # noqa: BLE001
                    logger.error(e)
                    self.disconnect(con)


ws_manager = WebSocketManager()
