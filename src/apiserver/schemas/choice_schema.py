from pydantic import BaseModel

class ChoiceCreate(BaseModel):
    question_id: str
    content: str

class ChoiceResponse(BaseModel):
    id: int
    question_id: str
    content: str
    created_at: str
