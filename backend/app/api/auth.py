from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DbDep
from app.config import settings
from app.models import User
from app.schemas.auth import LoginIn, MeOut
from app.services.auth import make_token, verify_password

router = APIRouter()

COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 gün


@router.post("/login", response_model=MeOut)
async def login(payload: LoginIn, response: Response, db: DbDep) -> MeOut:
    user = await db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "kullanıcı adı veya şifre hatalı")
    user.last_login = datetime.now(UTC)
    await db.commit()

    token = make_token(user.id, user.username)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.env != "dev",
        path="/",
    )
    return MeOut(id=user.id, username=user.username)


@router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUserDep) -> MeOut:
    return MeOut(id=user.id, username=user.username)
