"""Interviewer Copilot Agent - Interview support with short-term memory"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools.dynamodb_tools import get_user_profile
from tools.config import ToolConfig
from memory_hook import MemoryHook

app = BedrockAgentCoreApp()

agent = Agent(
    model=ToolConfig.CLAUDE_MODEL_ID,
    system_prompt="""You are an interview assistant that:
    
    **Question Generation:**
    - Technical questions: Assess coding, system design, problem-solving
    - Behavioral questions: Evaluate soft skills, teamwork, leadership
    - Situational questions: Test decision-making and judgment
    - Difficulty levels: Junior (1-3), Mid (4-6), Senior (7-10)
    
    **Question Format:**
    For each question provide:
    1. Question text
    2. Intent (what you're testing)
    3. Evaluation criteria (what to look for)
    4. Expected answer outline
    5. Follow-up questions (2-3)
    
    **Answer Evaluation:**
    Rate on 1-10 scale:
    - Completeness: Addresses all parts of question
    - Specificity: Concrete examples and details
    - Relevance: Stays on topic and demonstrates understanding
    - Communication: Clear, structured, professional
    
    **Feedback Format:**
    - Overall score (1-10)
    - Strengths (2-3 points)
    - Areas for improvement (2-3 points)
    - Recommended follow-ups
    
    Use get_user_profile to understand candidate background.""",
    tools=[get_user_profile],
    hooks=[MemoryHook()] if ToolConfig.MEMORY_ID else [],
    state={"session_id": "default"},
)


@app.entrypoint
def invoke(payload, context):
    """Support interview process with memory"""
    if hasattr(context, "session_id"):
        agent.state.set("session_id", context.session_id)

    action = payload.get("action", "generate_questions")
    user_id = payload.get("user_id")

    if action == "generate_questions":
        job_role = payload.get("job_role", "Software Engineer")
        interview_type = payload.get("interview_type", "technical")
        difficulty = payload.get("difficulty", "medium")
        count = payload.get("count", 5)

        prompt = f"""Generate {count} {interview_type} interview questions for {job_role} position.
Difficulty: {difficulty}
Candidate: user {user_id}

For each question include:
1. Question text
2. What you're testing (intent)
3. Evaluation criteria
4. Expected answer outline
5. 2-3 follow-up questions

Consider candidate's background from profile."""

    elif action == "evaluate_answer":
        question = payload.get("question", "")
        answer = payload.get("answer", "")
        job_context = payload.get("job_context", {})

        prompt = f"""Evaluate interview answer.

Question: {question}
Answer: {answer}
Job Context: {job_context}

Rate (1-10 scale):
1. Completeness
2. Specificity
3. Relevance
4. Communication

Provide:
- Overall score
- Strengths (2-3 points)
- Areas for improvement (2-3 points)
- Recommended follow-up questions"""

    elif action == "followup":
        prompt = """Based on the interview conversation so far, suggest 2-3 follow-up questions.

Consider:
- Areas that need deeper exploration
- Inconsistencies to clarify
- Strengths to showcase further
- Red flags to investigate"""

    else:
        prompt = payload.get("message", "How can I assist with the interview?")

    response = agent(prompt)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
