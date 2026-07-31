from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.bot.bot import bot
from src.config_reader import config
@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = config.WEBHOOK_URL
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    yield
    await bot.delete_webhook()
    await bot.session.close()
