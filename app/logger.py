from logging import INFO
from os import environ

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.add(
    'livechat_log.log',
    rotation='1 week',
    format='{time} {level} {message}',
    level='DEBUG',
    backtrace=True,
    diagnose=True
)


if sentry_dns := environ.get('SENTRY_DSN'):
    logger.info('Adding Sentry!')
    from sentry_sdk import init
    from sentry_sdk.integrations.logging import (
        EventHandler,
        LoggingIntegration,
    )

    init(
        dsn=sentry_dns,
        debug=True,
        enable_tracing=True,
        integrations=[LoggingIntegration()],
        traces_sample_rate=1.0,
    )

    logger.add(
        EventHandler(level=INFO),
        format='{time} {level} {message}',
        level='INFO',
    )
