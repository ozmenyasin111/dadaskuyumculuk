from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lazy import — döngüsel bağımlılıkları önle
    from app.services.bootstrap import bootstrap_admin_if_missing
    from app.workers.price_worker import start_price_worker, stop_price_worker

    await bootstrap_admin_if_missing()
    worker_task = await start_price_worker()
    try:
        yield
    finally:
        await stop_price_worker(worker_task)


fastapi_app = FastAPI(title="Dadaş Kuyumculuk API", lifespan=lifespan)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# REST routers
from app.api.auth import router as auth_router  # noqa: E402
from app.api.margins import router as margins_router  # noqa: E402
from app.api.prices import router as prices_router  # noqa: E402
from app.api.pricing_mode import router as pricing_mode_router  # noqa: E402
from app.api.users import router as users_router  # noqa: E402
from app.api.volatility import router as volatility_router  # noqa: E402

fastapi_app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
fastapi_app.include_router(prices_router, prefix="/api/prices", tags=["prices"])
fastapi_app.include_router(margins_router, prefix="/api/admin/margins", tags=["admin"])
fastapi_app.include_router(volatility_router, prefix="/api/admin/volatility", tags=["admin"])
fastapi_app.include_router(pricing_mode_router, prefix="/api/admin/pricing-mode", tags=["admin"])
fastapi_app.include_router(users_router, prefix="/api/admin/users", tags=["admin"])

# Socket.io mount — combined ASGI app
from app.socketio_app import sio  # noqa: E402

asgi = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
