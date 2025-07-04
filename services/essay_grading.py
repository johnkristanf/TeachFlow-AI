from core.openai_client import OpenAIClient
from repositories.essay_grading import EssayGradingRepository
import asyncio

class EssayGradingService:
    def __init__(self):
        self.client = OpenAIClient()
        self.repo = EssayGradingRepository()
        
    async def grade_essay_service(self, essay_id, essay: str, rubric_category, grade_level, grade_intensity, rubric_criteria: str):
        raw_grading_result = await self.client.grade_essay(essay, rubric_category, grade_level, grade_intensity, rubric_criteria)
        
        parsed_grading_result = self.client.parse_llm_response_to_json(raw_grading_result)
        
        
        evaluations = parsed_grading_result.get('evaluations')
        total_score = parsed_grading_result.get('total_score')
        max_total_score = parsed_grading_result.get('max_total_score')
        overall_feedback = parsed_grading_result.get('overall_feedback')
        
        print(f'- evaluations: {evaluations}')
        print(f'- total_score: {total_score}')
        print(f'- max_total_score: {max_total_score}')
        print(f'- overall_feedback: {overall_feedback}')
        
        # PROVIDES A NON_BLOCKING OPERATION OVER SYNCHRONOUS FUNCTIONS
        await asyncio.to_thread(self.repo.save_evaluations, essay_id, evaluations)
        await asyncio.to_thread(self.repo.save_summary, essay_id, total_score, max_total_score, overall_feedback)
        await asyncio.to_thread(self.repo.update_essay_raw_sql, essay_id, 'status', 'graded')
        
    def set_failed_grading_service(self, essay_id, failure_type: str, error_message: str, error_details: dict = None):
        self.repo.update_essay_raw_sql(essay_id, 'status', 'failed')
        self.repo.insert_grading_log(
            essay_id=essay_id,
            failure_type=failure_type,
            error_message=error_message,
            error_details=error_details,
        )
        
       