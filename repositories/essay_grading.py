import uuid
import json
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database.connect import SessionLocal
from models.essay_evaluations import EssayEvaluations
from models.essay_summaries import EssaySummaries
from datetime import datetime

class EssayGradingRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def __del__(self):
        # Basic cleanup, but consider explicit session management in your app's lifecycle
        if self.db:
            self.db.close()
        
    def save_evaluations(self, essay_id: str, evaluations: list[dict]):
        try:
            # 1. Delete existing evaluations for this essay_id
            print(f"Deleting existing evaluations for essay_id: {essay_id}")
            self.db.query(EssayEvaluations).filter(EssayEvaluations.essay_id == essay_id).delete()
            self.db.flush() # Flush to ensure deletes are processed before inserts

            # 2. Insert new evaluations
            print(f"Inserting new evaluations for essay_id: {essay_id}")
            for eval_data in evaluations:
                evaluation = EssayEvaluations(
                    id=str(uuid.uuid4()), # Generate new UUID for each evaluation
                    essay_id=essay_id,
                    criterion=eval_data.get("criterion"),
                    matched_label=eval_data.get("matched_label"),
                    score=eval_data.get("score"),
                    max_score=eval_data.get("max_score"),
                    reason=eval_data.get("reason"),
                    suggestion=eval_data.get("suggestion"),
                    created_at=datetime.now() # Use current time for new evaluations
                )
                self.db.add(evaluation)
            self.db.commit()
            print(f"Successfully saved new evaluations for essay {essay_id}.")

        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"SQLAlchemyError in save_evaluations for essay {essay_id}: {e}")
            raise # Re-raise the exception after rollback
        
    def save_summary(self, essay_id: str, total_score: int, max_total_score: int, overall_feedback: str):
        try:
            existing_summary = self.db.query(EssaySummaries).filter(EssaySummaries.essay_id == essay_id).first()


            if existing_summary:
                # If summary exists, update it
                print(f"Updating existing summary for essay_id: {essay_id}")
                existing_summary.total_score = total_score
                existing_summary.max_total_score = max_total_score
                existing_summary.overall_feedback = overall_feedback
            else:
                print(f"Creating new summary for essay_id: {essay_id}")
                summary = EssaySummaries(
                    id=str(uuid.uuid4()),
                    essay_id=essay_id,
                    total_score=total_score,
                    max_total_score=max_total_score,
                    overall_feedback=overall_feedback
                )
                self.db.add(summary)

            self.db.commit()
            print(f"Successfully saved/updated summary for essay {essay_id}.")
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise
        
    def update_essay_raw_sql(self, essay_id: str, column_name: str, new_value):
        
        try:
            sql = text(f"UPDATE essay SET {column_name} = :value WHERE id = :essay_id")
            self.db.execute(sql, {"value": new_value, "essay_id": essay_id})
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise
        
    def insert_grading_log(self, essay_id: str, failure_type: str, error_message: str, error_details: dict = None):
        """
        Inserts a new log entry into the essay_grading_logs table using raw SQL.
        """
        try:
            # Prepare the JSONB data. PostgreSQL expects JSONB as a string.
            # json.dumps converts Python dict to JSON string.
            error_details_json = json.dumps(error_details) if error_details else None

            sql = text(f"""
                INSERT INTO essay_grading_logs (
                    essay_id,
                    failure_type,
                    error_message,
                    error_details,
                    logged_at
                ) VALUES (
                    :essay_id,
                    :failure_type,
                    :error_message,
                    :error_details,
                    NOW() -- Use NOW() for the default timestamp as defined in Drizzle schema
                )
            """)

            # Execute the SQL with parameters
            self.db.execute(sql, {
                "essay_id": essay_id,
                "failure_type": failure_type,
                "error_message": error_message,
                "error_details": error_details_json, # Pass the JSON string
            })
            
            self.db.commit() # Commit the transaction after successful insert
            print(f"Logged grading failure for essay {essay_id} ({failure_type})")
            
        except SQLAlchemyError as e:
            self.db.rollback() 
            print(f"Error inserting grading log for essay {essay_id}: {e}")
            raise
