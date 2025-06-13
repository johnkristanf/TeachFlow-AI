import os 
import json
from openai import OpenAI, OpenAIError, APIConnectionError, Timeout, RateLimitError, AuthenticationError
from prompts.essay_grading import LLMPrompts
from exceptions import MalformedLLMResponseError


class OpenAIClient:
    def __init__(self, model: str = "gpt-4.1-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.prompts = LLMPrompts()
        
        
    def grade_essay(self, essay: str, rubric_criteria: str, max_tokens: int = 300) -> str:
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    self.prompts.system_essay_grading(), 
                    self.prompts.user_essay_grading(essay, rubric_criteria)
                ],
                
                max_tokens=max_tokens,
                temperature=0.2,
            )
            
            return response.choices[0].message.content
        
        except RateLimitError as e:
            print("🔁 Rate limit exceeded. Retry later.")
            raise

        except Timeout as e:
            print("⏰ OpenAI request timed out.")
            raise

        except APIConnectionError as e:
            print("🔌 Failed to connect to OpenAI API.")
            raise

        except AuthenticationError as e:
            print("🔒 Authentication with OpenAI API failed.")
            raise

        except OpenAIError as e:
            print("❌ OpenAI API error:", e)
            raise
        
        
    def parse_llm_response_to_json(self, response: str):
        try:
            clean_response = response.strip()
            parsed = json.loads(clean_response)
            return parsed
        
        except json.JSONDecodeError:
            raise MalformedLLMResponseError("LLM return malformed response")