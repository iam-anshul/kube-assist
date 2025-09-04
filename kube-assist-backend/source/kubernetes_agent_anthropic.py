from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from source.command import run_kubectl_command
from source.models import agentDeps
from dotenv import load_dotenv
import os
from source.system_prompts import assistant_agent_prompt
from pydantic_ai.models.anthropic import AnthropicModel
from source.summarise_agent import run_summarise_agent
from source.ai_model import model

load_dotenv()
API_KEY = os.getenv("ANTHRIPIC_API_KEY")

kubernetesAgent_ANTHROPIC = Agent(
    model=model,
    system_prompt=assistant_agent_prompt,
    retries=1
)

@kubernetesAgent_ANTHROPIC.tool(retries=1)
def run_command_anthropic(ctx: RunContext[agentDeps], command: str) -> str:
    "Use this function to run all the commands especially kubectl commands"
    return run_kubectl_command(command, ctx.deps.context_name, ctx.deps.kubeconfig_path, ctx.deps.access_key_id, ctx.deps.access_key)



