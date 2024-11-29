from contextlib import asynccontextmanager
from os import environ
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from .containers import Container
from .routes import app as app_router

load_dotenv()
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = environ['SERVICES'].split(',')
    if 'youtube' in services:
        await container.service_aggregation('youtube').start()
    if 'twitch' in services:
        await container.service_aggregation('twitch').start()

    yield


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(app_router)
app.container = container
