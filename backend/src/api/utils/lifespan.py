from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.bot.bot import bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = "https://ваш-домен.com/webhook"
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    yield
    await bot.delete_webhook()
    await bot.session.close()
