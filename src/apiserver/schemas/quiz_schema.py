from pydantic import BaseModel

class QuizAttemptCreate(BaseModel):
    title: str
    description: str
    created_by: str

class QuizAttemptResponse(BaseModel):
    id: int
    title: str
    description: str
    created_by: str
    created_at: str
    updated_at: str
