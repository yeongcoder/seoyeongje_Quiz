from pydantic import BaseModel

class AnswerCreate(BaseModel):
    attempt_id: str
    question_id: str
    choice_id: str

class AnswerResponse(BaseModel):
    id: int
    attempt_id: str
    question_id: str
    choice_id: str
    is_correct: bool
    answered_at: str
