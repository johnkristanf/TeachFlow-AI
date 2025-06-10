import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base

class EssayEvaluations(Base):
    __tablename__ = "essay_evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    essay_id = Column(String, unique=True)

    criterion = Column(String, nullable=True)
    matched_label = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    reason = Column(String, nullable=True)
    suggestion = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship to Essay model (assume defined elsewhere)
    # essay = relationship("Essay", back_populates="evaluations")
