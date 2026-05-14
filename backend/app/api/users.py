from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUserDep, DbDep
from app.models import User
from app.schemas.user import UserCreateIn, UserOut, UserPasswordIn
from app.services.auth import hash_password

router = APIRouter()


@router.get("", response_model=list[UserOut])
async def list_users(_user: CurrentUserDep, db: DbDep) -> list[UserOut]:
    rows = await db.scalars(select(User).order_by(User.id))
    return [UserOut.model_validate(r) for r in rows]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreateIn, _user: CurrentUserDep, db: DbDep) -> UserOut:
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "kullanıcı adı zaten var")
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.patch("/{user_id}/password", response_model=UserOut)
async def change_password(
    user_id: int, payload: UserPasswordIn, _user: CurrentUserDep, db: DbDep
) -> UserOut:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "kullanıcı bulunamadı")
    user.password_hash = hash_password(payload.password)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current: CurrentUserDep, db: DbDep) -> None:
    if user_id == current.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "kendi hesabınızı silemezsiniz")
    total = await db.scalar(select(func.count(User.id)))
    if total and total <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "son admin silinemez")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "kullanıcı bulunamadı")
    await db.delete(user)
    await db.commit()
