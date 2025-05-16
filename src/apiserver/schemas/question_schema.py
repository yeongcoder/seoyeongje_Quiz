from pydantic import BaseModel

class QuestionCreate(BaseModel):
    quiz_id: str
    content: str
    correct_choice_id: str

class QuestionResponse(BaseModel):
    id: int
    quiz_id: str
    content: str
    correct_choice_id: str
    created_at: str
