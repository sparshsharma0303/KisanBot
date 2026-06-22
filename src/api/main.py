from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router
from src.logger import logging

@asynccontextmanager
async def lifespan(app:FastAPI):
    logging.info("kisanbot api starting up")
    yield
    logging.info("kisanbot api shutting down")

app = FastAPI(
    title = "KisaBot API",
    description = "Multilingual Agriculutra RAG agent for Indian Farmers",
    version = "0.1.0",
    lifespan = lifespan
)

app.include_router(router)

@app.get("/")
def health_check():
    return {"status":"ok", "app": "KisanBot"}

