from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes import content_router, dashboard_router, tags_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Owly", lifespan=lifespan)

# Registers /tags under /api -> Results in /api/tags
app.include_router(tags_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(dashboard_router)


@app.get("api/health")
def health_check():
    return {"status": "ok"}
