from dotenv import load_dotenv
import os
from pydantic_ai.models.anthropic import AnthropicModel

load_dotenv()
API_KEY = os.getenv("ANTHRIPIC_API_KEY")

model = AnthropicModel('claude-3-5-sonnet-latest', api_key=API_KEY)
