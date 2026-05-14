"""Socket.io AsyncServer (handler'lar burada). ASGI bütünleşik uygulama main.py'de
oluşturulur — modüller arası döngüsel import'u önlemek için."""

import socketio

from app.config import settings

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origin_list,
)


@sio.event
async def connect(sid: str, environ: dict) -> None:
    # Şu an public yayın; ileride apiKey ile auth gerekirse environ'daki query string kontrol.
    pass


@sio.event
async def disconnect(sid: str) -> None:
    pass
