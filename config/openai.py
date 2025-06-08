from openai import OpenAI
from os import getenv

def load_openai_client():
    client = OpenAI(
        api_key = getenv('OPENAI_API_KEY'),
        max_retries=10
    )

    return client