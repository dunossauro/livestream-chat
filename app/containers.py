from asyncio import get_event_loop
from dependency_injector import containers, providers
from .ws_manager import WebSocketManager
from .services import Youtube, Twitch


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=['app.app', 'app.routes', 'app.services']
    )

    # container.config.from_pydantic(Settings())

    loop = providers.Callable(get_event_loop)

    ws_manager = providers.Singleton(WebSocketManager)

    service_aggregation = providers.Aggregate(
        twitch=providers.Factory(Twitch, loop=loop, ws_manager=ws_manager),
        youtube=providers.Factory(  # type: ignore
            Youtube, loop=loop, ws_manager=ws_manager
        ),
    )
