import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from apiserver.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"))
    content = Column(Text, nullable=False)
    correct_choice_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    quiz = relationship("Quiz", back_populates="questions")
    choices = relationship("Choice", back_populates="question")