from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from apiserver.db.database import AsyncSessionLocal
from apiserver.models.user_model import User
from apiserver.schemas.user_shcema import UserCreate
from apiserver.utils.auth import hash_password
from sqlalchemy.future import select

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/users")
async def post_users(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = User(
        name = user_data.name,
        email = user_data.email,
        password = hash_password(user_data.password),
        is_admin = user_data.is_admin,
    )
    db.add(user)
    await db.commit() 
    await db.refresh(user)

    return user