from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# 퀴즈 생성용
class QuizCreate(BaseModel):
    title: str
    description: Optional[str]
    num_questions: int
    shuffle_questions: bool = False
    shuffle_choices: bool = False

# 퀴즈 목록 응답
class QuizOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True

# 퀴즈 상세 응답
class ChoiceOut(BaseModel):
    id: UUID
    content: str

    class Config:
        orm_mode = True

class QuestionOut(BaseModel):
    id: UUID
    content: str
    choices: List[ChoiceOut]

    class Config:
        orm_mode = True

class QuizDetailOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    questions: List[QuestionOut]

    class Config:
        orm_mode = True

# 응시 요청
class QuizAttemptRequest(BaseModel):
    answers: List[UUID]  # 선택한 choice_id 리스트

# 응시 결과 응답
class QuizAttemptResponse(BaseModel):
    score: int
    total: int
    submitted_at: datetime
