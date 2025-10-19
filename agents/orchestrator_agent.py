"""Orchestrator Agent - Main coordinator for all recruitment agents"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools.agent_tools import (
    call_concierge,
    call_skill_parser,
    call_job_matcher,
    call_interviewer,
)
from tools.config import ToolConfig
from memory_hook import MemoryHook

app = BedrockAgentCoreApp()

agent = Agent(
    model=ToolConfig.CLAUDE_MODEL_ID,
    system_prompt="""You are the main coordinator for an AI recruitment platform. Route user requests to specialized agents:

    - call_concierge: Career consultation, job search, general questions
    - call_skill_parser: Resume analysis, GitHub profile evaluation
    - call_job_matcher: Match candidates with jobs, calculate scores
    - call_interviewer: Interview questions, evaluation, follow-ups
    
    Analyze user intent and call the appropriate agent(s). You can chain multiple agents if needed.""",
    tools=[call_concierge, call_skill_parser, call_job_matcher, call_interviewer],
    hooks=[MemoryHook()] if ToolConfig.MEMORY_ID else [],
    state={"session_id": "default"},
)


@app.entrypoint
def invoke(payload, context):
    """Orchestrate recruitment workflow"""
    if hasattr(context, "session_id"):
        agent.state.set("session_id", context.session_id)

    user_id = payload.get("user_id", "guest")
    request = payload.get("request", "Hello")
    
    # Include user_id in the prompt for context
    prompt = f"User ID: {user_id}\nRequest: {request}"
    
    response = agent(prompt)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
