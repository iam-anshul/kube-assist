import asyncio
from source.kubernetes_agent_anthropic import kubernetesAgent_ANTHROPIC
from pydantic_ai.messages import ModelMessage, ModelResponse, ModelRequest, TextPart, UserPromptPart, ToolCallPart, ToolReturnPart

mhistory = []

async def run_start_agent():
    async with kubernetesAgent_ANTHROPIC.run_stream(input("Prompt:- ")) as response:
        async for text in response.stream():
            print(response.new_messages_json())
            mhistory.append(response.all_messages())
    
        while True:
            response = kubernetesAgent_ANTHROPIC.run_stream(input("Prompt:- "), message_history=mhistory[-1])
            mhistory.append(response.all_messages())
            print(response.data)

if __name__ == "__main__":
    #asyncio.run(main())
    asyncio.run(run_start_agent())


# how many pods are there in default namespace ?

# is there any pvc in default namespace?