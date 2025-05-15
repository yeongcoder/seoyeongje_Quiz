import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from apiserver.db.base import Base

class QuizConfig(Base):
    __tablename__ = "quiz_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), unique=True)
    num_questions  = Column(Integer, nullable=False)
    shuffle_questions  = Column(Boolean, default=False)
    shuffle_choices  = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    quiz = relationship("Quiz", back_populates="config")