from pydantic import BaseModel

class QuizAttemptCreate(BaseModel):
    quiz_id: str
    num_questions: int
    shuffle_questions: bool
    shuffle_choices: bool

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: str
    num_questions: int
    shuffle_questions: bool
    shuffle_choices: bool
    created_at: str
