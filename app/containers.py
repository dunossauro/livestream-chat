from dependency_injector import containers, providers
from .ws_manager import WebSocketManager


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=['app.app', 'app.routes']
    )
    ws_manager = providers.Singleton(WebSocketManager)
