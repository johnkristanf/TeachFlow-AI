
class LLMPrompts:
    
    def system_essay_grading(self):
        return {
                "role": "system",
                "content": (
                    "You are a professional academic essay grader. You will be given an essay "
                    "and a grading rubric in JSON format. For each criterion in the rubric:\n"
                    
                    """
                    **Your Tasks**:
                        1. The essay may come from OCR (scanned image). First, clean up formatting and minor grammar issues, such as:
                            - Fix strange line breaks and misused punctuation.
                            - Correct common OCR mistakes (e.g., 'bo' → 'to', 'esources' → 'resources').
                            - Make the essay more readable without changing the student’s tone or intent.
                            - Do NOT rewrite or over-edit. Only correct what's needed for clarity.
        
                        2. For **each criterion**, select the performance level that best reflects the quality of the essay.
                        3. Extract and return:
                            - The `criterion` title.
                            - The selected performance level's `label`.
                            - The assigned `score`.
                            - The `max_score` possible for that criterion (use the highest score from that criterion’s levels).
                            
                            - A short but clear `reason` explaining why the score was assigned.
                                **Be specific. Quote or reference exact words, phrases, or sentences from the essay that influenced your decision.**
                            
                            - A helpful `suggestion` to improve that specific aspect.
                        4. After evaluating all criteria, compute the **overall total score** out of the **maximum possible score**, like `12 / 20`.
                        5. Provide an `overall_feedback` summary that reflects the essay's strengths and areas for improvement across all criteria.
                    """
                )
            }
        
    def user_essay_grading(self, essay: str, rubric_criteria: str):
        return {
                "role": "user",
                "content": f"""
                    Essay:
                    \"\"\"
                    {essay}
                    \"\"\"

                    Rubric Criteria (JSON):
                    {rubric_criteria}

                    "Return only a valid JSON object in the format below — do not include any explanation, markdown, or commentary:"
                    {{
                        "evaluations": [
                            {{
                                "criterion": "Thesis & Focus",
                                "matched_label": "Good",
                                "score": 3,
                                "max_score": 4,
                                "reason": "The thesis is clear but lacks deeper insight.",
                                "suggestion": "Refine the thesis to be more specific and analytical."
                            }},
                            ...
                        ],
                        
                        "total_score": 12,
                        "max_total_score": 20,
                        "overall_feedback": "The essay is generally well-organized and grammatically sound but could benefit from a sharper thesis and improved transitions."
                    }}
                """
            }