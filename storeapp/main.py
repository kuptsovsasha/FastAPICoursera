from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from storeapp.databse import database
from storeapp.logging_conf import configure_logging
from storeapp.routers.post import router as post_router
from storeapp.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router, prefix="/posts")
app.include_router(user_router, prefix="/users")
