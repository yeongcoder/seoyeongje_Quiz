from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# POST /
class ChoiceCreate(BaseModel):
    content: str
    is_correct: bool

class QuestionCreate(BaseModel):
    content: str
    choices: List[ChoiceCreate]

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, v):
        if not any(choice.is_correct for choice in v):
            raise ValueError("At least one choice must be marked as correct.")
        return v

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
    
class QuizCreateResponse(BaseModel):
    quiz_id: UUID
    message: str


# GET /
class QuizConfig(BaseModel):
    quiz_id: UUID
    num_questions: int
    shuffle_choices: bool
    id: UUID
    shuffle_questions: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class QuizResponse(BaseModel):
    title: str
    description: str
    created_at: datetime
    id: UUID
    created_by: UUID
    updated_at: datetime
    config: Optional[QuizConfig]
    attempted: bool

    model_config = {
        "from_attributes": True,
    }

class QuizGetListResponse(BaseModel):
    quizzes: List[QuizResponse]
    total_pages: int
    page: int
    per_page: int

    class Config:
        orm_mode = True


# PATCH /{quiz_id}
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
    quiz_id: UUID
    message: str


# GET /{quiz_id}/forstaff
class QuestionChoice(BaseModel):
    created_at: datetime
    id: UUID
    question_id: UUID
    content: str
    
    model_config = {
        "from_attributes": True,
    }
    
class Question(BaseModel):
    id: UUID
    correct_choice_id: UUID
    quiz_id: UUID
    content: str
    created_at: datetime
    choices: List[QuestionChoice]

    model_config = {
        "from_attributes": True,
    }

class QuizGetDetailForStaffResponse(BaseModel):
    title: str
    description: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    config: QuizConfig
    questions: List[Question]
    total_pages: int
    page: int
    per_page: int

    class Config:
        orm_mode = True


# POST /{quiz_id}/attempt
class QuizAttemptResponse(BaseModel):
    attempt_id: UUID 
    message: str


# GET /{quiz_id}/foruser
class QuizQuestionChoice(BaseModel):
    id: UUID
    content: str
    selected: bool
    
    model_config = {
        "from_attributes": True,
    }

class QuizQuestion(BaseModel):
    id: UUID
    content: str
    correct_choice_id: Optional[UUID]
    choices: List[QuizQuestionChoice]
    
    model_config = {
        "from_attributes": True,
    }

class QuizGetDetailForUserResponse(BaseModel):
    id: UUID
    title: str
    description: str
    page: int
    per_page: int
    total_pages: int
    questions: List[QuizQuestion]
    
    class Config:
        orm_mode = True

# POST /{quiz_id}/answer
class QuizAnswer(BaseModel):
    question_id: UUID
    choice_id: UUID

class QuizAnswerCreate(BaseModel):
    answer: List[QuizAnswer]

class QuizAnswerCreateResponse(BaseModel):
    attempt_id: UUID
    message: str

# POST /{quiz_id}/submit
class QuizSubmitResponse(BaseModel):
    attempt_id: UUID
    score: int
    submitted_at: datetime