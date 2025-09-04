from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from source.command import run_kubectl_command
from dotenv import load_dotenv
import os
from source.system_prompts import assistant_agent_prompt
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from source.models import agentDeps

load_dotenv()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_KEY = os.getenv("OPENAI_KEY")

model = OpenAIModel("gpt-4o", provider=OpenAIProvider(base_url="https://api.openai.com/v1", api_key=OPENAI_KEY))

kubernetesAgent_OPENAI = Agent(
    model,
    system_prompt=assistant_agent_prompt,
    retries=3
)

@kubernetesAgent_OPENAI.tool()
def run_command_openai(ctx: RunContext[agentDeps], command: str) -> str:
    "Use this function to run all the commands especially kubectl commands"
    return run_kubectl_command(command, ctx.deps.context_name, ctx.deps.kubeconfig_path, ctx.deps.access_key_id, ctx.deps.access_key)















