from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache.backends.inmemory import InMemoryBackend

import books
import users
from common.persistance import create_db_and_tables

from fastapi_cache import FastAPICache

@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(InMemoryBackend())
    create_db_and_tables()
    yield


app = FastAPI(title="Library Management API", lifespan=lifespan)

app.include_router(users.router)
app.include_router(books.router)
