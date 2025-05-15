import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from apiserver.db.base import Base


class Choice(Base):
    __tablename__ = "choices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    question = relationship("Question", back_populates="choices")