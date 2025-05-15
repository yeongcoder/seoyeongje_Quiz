from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from apiserver.db.database import AsyncSessionLocal
from apiserver.models.user_model import User
from sqlalchemy.future import select

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
