"""Socket.io üzerinden frontend'e fiyat yayını."""

from dataclasses import asdict

from app.services.cache import cache
from app.socketio_app import sio


async def broadcast_prices() -> None:
    state = cache.get_prices()
    payload = {
        "fiyatlar": [asdict(r) for r in state.rows],
        "pariteler": state.pariteler,
        "guncellendi": state.guncellendi,
        "healthy": state.healthy,
    }
    await sio.emit("prices", payload)
