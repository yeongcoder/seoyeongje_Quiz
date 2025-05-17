from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# 문항 생성용
class ChoiceCreate(BaseModel):
    content: str
    is_correct: bool

# 문제 생성용
class QuestionCreate(BaseModel):
    content: str
    choices: List[ChoiceCreate]

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, v):
        if not any(choice.is_correct for choice in v):
            raise ValueError("At least one choice must be marked as correct.")
        return v

# 퀴즈 생성용
class QuizCreate(BaseModel):
    title: str
    description: Optional[str]
    num_questions: int
    shuffle_questions: bool = False
    shuffle_choices: bool = False
    questions: List[QuestionCreate]

    @field_validator("questions", mode="after")
    @classmethod
    def validate_questions(cls, v):
        if len(v) < 2:
            raise ValueError("At least two questions are required.")
        return v

# 퀴즈 수정용
class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    num_questions: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_choices: Optional[bool] = None
    questions: Optional[List[QuestionCreate]] = None

    @field_validator("questions", mode="after")
    @classmethod
    def validate_questions(cls, v):
        if len(v) < 2:
            raise ValueError("At least two questions are required.")
        return v

class QuizUpdateResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True

class QuizConfig(BaseModel):
    id: UUID
    quiz_id: UUID
    num_questions: int
    shuffle_questions: bool
    shuffle_choices: bool
    created_at: datetime

# 퀴즈 목록 응답
class QuizOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    attempted: Optional[bool]
    config: Optional[QuizConfig]
    created_by: Optional[UUID]
    updated_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# 퀴즈 상세 응답
class ChoiceOut(BaseModel):
    id: UUID
    content: str
    selected: bool

    class Config:
        orm_mode = True

# 문제 응답
class QuestionOut(BaseModel):
    id: UUID
    content: str
    correct_choice_id: UUID | None
    choices: List[ChoiceOut]

    class Config:
        orm_mode = True

# 퀴즈 상세 응답
class QuizDetailOut(BaseModel):
    id: UUID
    title: str
    description: str
    page: int
    per_page: int
    total_pages: int
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

# 퀴즈 응시 생성용 답변
class AnswerCreate(BaseModel):
    question_id: UUID
    choice_id: UUID

# 응시내용 임시저장
class AnswerSave(BaseModel):
    answer: List[AnswerCreate]