from pydantic import BaseModel

class QuizAttemptCreate(BaseModel):
    user_id: str
    quiz_id: str
    started_at: str
    score: int

class QuizAttemptSubmit(BaseModel):
    submitted_at: str

class QuizAttemptResponse(BaseModel):
    id: int
    user_id: str
    quiz_id: str
    started_at: str
    submitted_at: str
    score: int
    created_at: str
