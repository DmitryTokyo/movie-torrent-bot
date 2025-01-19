import asyncio
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bot.bot import run_bot

logging.config.fileConfig('logging.cfg')
logger = logging.getLogger('kinoTorrent')

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(run_bot())
    yield

app = FastAPI(lifespan=lifespan)
