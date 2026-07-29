from fastapi import FastAPI
from src.api.utils.lifespan import lifespan
from src.api.handlers.user_handler import router as user_router
app = FastAPI(lifespan=lifespan)

app.include_router(user_router)