"""Ortak FastAPI dependency'leri."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User
from app.services.auth import decode_token

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def current_user(
    db: DbDep,
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> User:
    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "oturum yok")
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token geçersiz")
    user = await db.get(User, int(payload.get("sub", 0)))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "kullanıcı bulunamadı")
    return user


CurrentUserDep = Annotated[User, Depends(current_user)]
