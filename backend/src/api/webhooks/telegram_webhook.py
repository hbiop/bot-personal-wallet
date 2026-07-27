from fastapi import APIRouter
from fastapi import Request, status
from aiogram import types
from src.bot.bot import bot
from src.bot.dispatcher import dispatcher as dp

router = APIRouter()

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(request: Request):
    webhook_data = await request.json()
    tg_update = types.Update.model_validate(webhook_data, context={"bot": bot})
    await dp.feed_update(bot, tg_update)
    return {"status": "ok"}