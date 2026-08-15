from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.crud.user import get_tenant_by_slug, get_user_by_email, create_user
from app.schemas.auth import UserRegister, UserLogin, UserOut, Token, RefreshRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    tenant = await get_tenant_by_slug(db, payload.tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=404, detail="مستاجر یافت نشد.")

    if await get_user_by_email(db, tenant.id, payload.email):
        raise HTTPException(status_code=409, detail="کاربر با این ایمیل قبلا ثبت شده است.")

    user = await create_user(
        db,
        tenant_id=tenant.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    tenant = await get_tenant_by_slug(db, payload.tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=401, detail="اطلاعات ورود نامعتبر است.")

    user = await get_user_by_email(db, tenant.id, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="اطلاعات ورود نامعتبر است.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="حساب کاربری غیرفعال است.")

    access_token = create_access_token(str(user.id), str(tenant.id))
    refresh_token = create_refresh_token(str(user.id), str(tenant.id))
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if data is None or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token نامعتبر است.")

    access_token = create_access_token(data["sub"], data["tenant_id"])
    refresh_token = create_refresh_token(data["sub"], data["tenant_id"])
    return Token(access_token=access_token, refresh_token=refresh_token)
