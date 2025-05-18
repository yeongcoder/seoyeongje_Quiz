# apiserver/src/apiserver/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from apiserver.db.database import get_db
from apiserver.models.user_model import User
from apiserver.utils.auth import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.name == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, hash_password(form_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
