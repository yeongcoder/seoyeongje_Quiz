from fastapi import Depends, APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession
from apiserver.db.database import AsyncSessionLocal
from apiserver.models.user_model import User
from apiserver.schemas.user_shcema import UserCreate
from apiserver.utils.auth import hash_password
from sqlalchemy.future import select
from apiserver.dependencies.auth import get_current_user, admin_required
from sqlalchemy.orm import class_mapper
from sqlalchemy import func
from apiserver.db.redis_client import redis_client
import json

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/users")
async def get_users(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    
    redis_key = str(request.url.path) + "?" + str(request.url.query)

    cached_data = await redis_client.get(redis_key)
    if cached_data:
        return json.loads(cached_data)

    count_result = await db.execute(
        select(func.count(User.id))
    )
    total = count_result.scalar()
    offset = (page - 1) * per_page
    total_pages = round(total/per_page)

    columns = [column for column in class_mapper(User).columns if column.name != 'password']
    result = await db.execute(
        select(*columns)
        .offset(offset)
        .limit(per_page)
    )
    users = [dict(row._mapping) for row in result.all()]

    response_data = {
        "users": users,
        "total_pages": total_pages,
        "page": page,
        "per_page": per_page
    }

    await redis_client.set(redis_key, json.dumps(response_data, default=str), ex=60)

    return response_data

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