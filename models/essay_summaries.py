from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.connect import Base
import uuid

class EssaySummaries(Base):
    __tablename__ = "essay_summaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    essay_id = Column(Integer, unique=True)  # one-to-one relationship

    total_score = Column(Integer, nullable=True)
    max_total_score = Column(Integer, nullable=True)
    overall_feedback = Column(String, nullable=True)

    # Back-reference to Essay
    # essay = relationship("Essay", back_populates="summary")
