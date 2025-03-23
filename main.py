from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import books
import users
from common.persistance import create_db_and_tables
from common.rate_limiter import limiter

@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(InMemoryBackend())
    create_db_and_tables()
    yield
app = FastAPI(title="Library Management API", lifespan=lifespan)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(users.router)
app.include_router(books.router)
