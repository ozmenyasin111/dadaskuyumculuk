#!/bin/sh
set -e

echo "[start] container starting at $(date -u)"
echo "[start] PORT=${PORT:-(unset)}"
echo "[start] ENV=${ENV:-(unset)}"
echo "[start] DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo yes || echo no)"
echo "[start] FINANSVERI_API_KEY set: $([ -n "$FINANSVERI_API_KEY" ] && echo yes || echo no)"

echo "[start] running alembic upgrade head..."
alembic upgrade head
echo "[start] alembic exit ok"

echo "[start] testing app.main import..."
python -u -c "import app.main; print('[start] app.main import OK')" || {
  echo "[start] APP IMPORT FAILED — see traceback above"
  exit 1
}

echo "[start] launching uvicorn on 0.0.0.0:${PORT}..."
exec python -u -m uvicorn app.main:asgi --host 0.0.0.0 --port "${PORT}" --proxy-headers --log-level info
