from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.api import api_router
from .database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set up resources
    create_db_and_tables()
    yield
    # Clean up resources


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
