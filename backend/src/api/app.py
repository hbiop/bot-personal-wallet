from fastapi import FastAPI
from src.utils.lifespan import lifespan

app = FastAPI(lifespan=lifespan)