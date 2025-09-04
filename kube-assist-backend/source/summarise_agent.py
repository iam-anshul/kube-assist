from source.ai_model import model
from pydantic_ai import Agent
from source.system_prompts import summarise_agent_prompt
from pydantic import BaseModel

class summariseResponseFormat(BaseModel):
    summary: str
    summarisation_required: bool

summariseAgent = Agent(
    model=model,
    result_type=summariseResponseFormat,
    system_prompt=summarise_agent_prompt,
    retries=3,
)

def run_summarise_agent(history: str):
    response = summariseAgent.run_sync(history)
    return response.data.summary, response.data.summarisation_required
    












