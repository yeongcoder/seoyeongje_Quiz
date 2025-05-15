# tools/create_tables.py
import sys
import os

# src 디렉토리를 Python path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import asyncio
from apiserver.db.database import engine
from apiserver.db.base import Base
from apiserver.models.user_model import User  # 테이블이 정의된 모델들 import
from apiserver.models.answer_model import Answer  # 테이블이 정의된 모델들 import
from apiserver.models.choice_model import Choice  # 테이블이 정의된 모델들 import
from apiserver.models.question_model import Question  # 테이블이 정의된 모델들 import
from apiserver.models.quiz_attempt_model import QuizAttempt  # 테이블이 정의된 모델들 import
from apiserver.models.quiz_config_model import QuizConfig  # 테이블이 정의된 모델들 import
from apiserver.models.quiz_model import Quiz  # 테이블이 정의된 모델들 import

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
