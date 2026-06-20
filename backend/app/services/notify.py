"""Telegram bildirimi — finansveri eksik/0 veri başladığında ve düzeldiğinde uyarı.

Token/chat id boşsa (env ayarlanmamışsa) sessizce devre dışıdır; hata fırlatmaz.
Worker döngüsünü bloklamamak için fire-and-forget (asyncio.create_task) çağrılır.
"""

import logging

import httpx

from app.config import settings

log = logging.getLogger("notify")


async def notify_telegram(text: str) -> None:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        return  # yapılandırılmamış → atla
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            if resp.status_code != 200:
                log.warning("telegram bildirimi başarısız: %s %s", resp.status_code, resp.text[:200])
    except Exception:
        log.warning("telegram bildirimi gönderilemedi", exc_info=True)
