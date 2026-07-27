from aiogram import Bot
from src.utils.config_reader import config


bot = Bot(token=config.BOT_TOKEN)