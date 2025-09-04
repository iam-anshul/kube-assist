from fastapi import Depends, APIRouter, HTTPException
from pydantic_ai import Agent
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from source.routes.kube_config.kubeconfig import get_context_names, get_access_key_and_id
from source.kubernetes_agent_anthropic import agentDeps
from source.routes.chat.crud import add_chatID_entry, add_message, render_chat, delete_chatID_entry, get_conversation
from source.routes.admin.admin_routes import get_history
from uuid import uuid4, UUID
from source.kubernetes_agent_anthropic import kubernetesAgent_ANTHROPIC
from source.kubernetes_agent_openai import kubernetesAgent_OPENAI
from pydantic_ai.messages import (
    TextPart,
    PartStartEvent,
    PartDeltaEvent,
    TextPartDelta
)
from fastapi.responses import StreamingResponse
import json
from source.models import chatRequest
import asyncio
from collections import defaultdict
from asyncio import Queue
from source.models import AddTaskRequest
from source.routes.tasks.task import add_task, update_task_status_entry
import os

# Store output buffers and flags for run_ids
agent_outputs = defaultdict(Queue)  # run_id -> Queue for streaming lines
agent_done_flags = dict()           # run_id -> True when done

chat_router = APIRouter()
    

@chat_router.get('/get-chat')
async def get_chat(chat_id: UUID, session: SessionContainer = Depends(verify_session())):
    conversation =  get_conversation(chat_id, session.get_user_id())
    
    return conversation

@chat_router.get('/get-user-chats')
async def get_chat_ids(session: SessionContainer = Depends(verify_session())):
    print(render_chat(session.get_user_id()))
    return render_chat(session.get_user_id())

@chat_router.post('/create-chat')
async def create_chat(project_id: UUID, session: SessionContainer = Depends(verify_session())) -> UUID:
    return add_chatID_entry(session.get_user_id(), project_id)

@chat_router.get('/stream-response')
async def stream_response(run_id: str):
    async def stream():
        queue = agent_outputs[run_id]
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=5.0)
                yield item.encode('utf-8') + b'\n'
            except asyncio.TimeoutError:
                if agent_done_flags.get(run_id):
                    break  # No more data, agent is done
    return StreamingResponse(stream(), media_type="text/plain")

@chat_router.post('/run-agent')
async def run_agent(request: chatRequest, session: SessionContainer = Depends(verify_session())):
    run_id = str(uuid4())

    # Fire off the agent in the background
    asyncio.create_task(run_agent_background(request.chat_id, request.project_id, run_id, request, session))
    
    return {"run_id": run_id}

async def run_agent_background(chat_id, project_id, run_id: str, request: chatRequest, session: SessionContainer):
    add_task(AddTaskRequest(chat_id=chat_id, project_id=project_id, task_id=run_id), session)
    buffer = ""  # Accumulated content
    userID = session.get_user_id()

    try:
        messages = await get_history(request.chat_id, session.get_access_token())
        kubeconfigPath = os.path.expanduser(f"~/.server_kubeconfigs/{userID}_configs/{project_id}/config")
        access_key_id, access_key = get_access_key_and_id(os.path.expanduser(f"~/.cloud_creds/{userID}_configs/{project_id}/credentials"))
        tool_dependency = agentDeps(context_name=get_context_names(path=kubeconfigPath), kubeconfig_path=kubeconfigPath, access_key_id=str(access_key_id), access_key=str(access_key))

        if request.model=="anthropic":
            async with kubernetesAgent_ANTHROPIC.iter(request.prompt, message_history=messages, deps=tool_dependency) as run:
                async for node in run:
                    if Agent.is_model_request_node(node):
                        async with node.stream(run.ctx) as request_stream:
                            async for event in request_stream:
                                if isinstance(event, PartStartEvent):
                                    content = event.part.content if isinstance(event.part, TextPart) else ""
                                    buffer += content
                                    await agent_outputs[run_id].put(json.dumps({
                                        "event": event.event_kind,
                                        "content": buffer
                                    }))
                                elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                    content_delta = event.delta.content_delta
                                    buffer += content_delta
                                    await agent_outputs[run_id].put(json.dumps({
                                        "event": event.event_kind,
                                        "content": buffer,
                                        "kind": "response"
                                    }))

                    elif Agent.is_end_node(node):
                        # Send the final message
                        await agent_outputs[run_id].put(json.dumps({
                            "done": True,
                            "content": buffer
                        }))
                        add_message(session.get_user_id(), request.chat_id, run.result.new_messages_json(), {
                            "query": request.prompt,
                            "content": buffer,
                        }, request.project_id)
        
        elif request.model=="openai":
            async with kubernetesAgent_OPENAI.iter(request.prompt, message_history=messages, deps=tool_dependency) as run:
                async for node in run:
                    if Agent.is_model_request_node(node):
                        async with node.stream(run.ctx) as request_stream:
                            async for event in request_stream:
                                if isinstance(event, PartStartEvent):
                                    content = event.part.content if isinstance(event.part, TextPart) else ""
                                    buffer += content
                                    await agent_outputs[run_id].put(json.dumps({
                                        "event": event.event_kind,
                                        "content": buffer
                                    }))
                                elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                    content_delta = event.delta.content_delta
                                    buffer += content_delta
                                    await agent_outputs[run_id].put(json.dumps({
                                        "event": event.event_kind,
                                        "content": buffer,
                                        "kind": "response"
                                    }))

                    elif Agent.is_end_node(node):
                        # Send the final message
                        await agent_outputs[run_id].put(json.dumps({
                            "done": True,
                            "content": buffer
                        }))
                        add_message(session.get_user_id(), request.chat_id, run.result.new_messages_json(), {
                            "query": request.prompt,
                            "content": buffer,
                        }, request.project_id)
        else:
            raise Exception(f"Model invalid")
            
        update_task_status_entry(userID, run_id, "Success")

    except Exception as e:
        update_task_status_entry(session.get_user_id(), run_id, "Failed")
        raise HTTPException(status_code=400, detail=f'Error in agent run: {e}')

    finally:
        agent_done_flags[run_id] = True


@chat_router.delete('/delete-chat')
async def delete_chat(chat_id: UUID, session: SessionContainer = Depends(verify_session())) -> UUID:
    deleted_chat = delete_chatID_entry(chat_id)
    if deleted_chat == None:
        raise HTTPException(status_code=400, detail='The given chat id does not exits')
        
    return deleted_chat
