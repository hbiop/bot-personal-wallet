from aiogram import Bot

from src.config_reader import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())