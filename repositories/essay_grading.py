import uuid

from sqlalchemy import text
from database.connect import SessionLocal
from models.essay_evaluations import EssayEvaluations
from models.essay_summaries import EssaySummaries
from datetime import datetime

class EssayGradingRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def save_evaluations(self, essay_id: str, evaluations: list[dict]):
        for eval_data in evaluations:
            evaluation = EssayEvaluations(
                id=str(uuid.uuid4()),
                essay_id=essay_id,
                criterion=eval_data.get("criterion"),
                matched_label=eval_data.get("matched_label"),
                score=eval_data.get("score"),
                max_score=eval_data.get("max_score"),
                reason=eval_data.get("reason"),
                suggestion=eval_data.get("suggestion"),
                created_at=datetime.now()
            )
            self.db.add(evaluation)
        self.db.commit()
        
    def save_summary(self, essay_id: str, total_score: int, max_total_score: int, overall_feedback: str):
        summary = EssaySummaries(
            id=str(uuid.uuid4()),
            essay_id=essay_id,
            total_score=total_score,
            max_total_score=max_total_score,
            overall_feedback=overall_feedback
        )
        
        self.db.add(summary)
        self.db.commit()
        
    def update_essay_raw_sql(self, essay_id: str, column_name: str, new_value):
        # Beware: Make sure column_name is validated or hardcoded to avoid SQL injection
        sql = text(f"UPDATE essay SET {column_name} = :value WHERE id = :essay_id")
        self.db.execute(sql, {"value": new_value, "essay_id": essay_id})
        self.db.commit()