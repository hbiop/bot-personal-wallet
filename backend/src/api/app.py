from fastapi import FastAPI
from src.api.utils.lifespan import lifespan
from src.api.handlers.user_handler import router as user_router
from src.api.handlers.transaction_handler import router as transaction_router
from src.api.webhooks.telegram_webhook import router as telegram_router
app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(telegram_router)