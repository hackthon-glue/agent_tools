"""Candidate Concierge Agent - Career consultation and job search support"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools.dynamodb_tools import get_user_profile, get_job_listings
from tools.collector_tools import search_job_market, search_company_info
from tools.config import ToolConfig
from memory_hook import MemoryHook

app = BedrockAgentCoreApp()

agent = Agent(
    model=ToolConfig.CLAUDE_MODEL_ID,
    system_prompt="""You are a friendly career concierge helping candidates with:
    
    **Career Consultation:**
    - Provide personalized career advice based on experience and goals
    - Analyze career trajectory and suggest growth paths
    - Address specific career concerns with actionable recommendations
    
    **Job Search Support:**
    - Find suitable positions matching skills and preferences
    - Research companies and provide insights
    - Recommend application strategies
    
    **Evaluation Criteria:**
    - Skills alignment with career goals
    - Market demand and growth potential
    - Work-life balance considerations
    - Company culture fit
    
    Use get_user_profile to understand the candidate's background.
    Use get_job_listings to find suitable positions from DB.
    Use search_job_market to search external job postings.
    Use search_company_info to research companies.""",
    tools=[get_user_profile, get_job_listings, search_job_market, search_company_info],
    hooks=[MemoryHook()] if ToolConfig.MEMORY_ID else [],
    state={"session_id": "default"},
)


@app.entrypoint
def invoke(payload, context):
    """Handle concierge agent requests with memory"""
    if hasattr(context, "session_id"):
        agent.state.set("session_id", context.session_id)

    action = payload.get("action", "general")
    user_id = payload.get("user_id")
    message = payload.get("message", "")

    if action == "career_consultation":
        career_history = payload.get("career_history", [])
        prompt = f"""Provide career consultation for user {user_id}.
        
Question: {message}
Career History: {career_history if career_history else 'Not provided'}

Provide:
1. Analysis of current situation
2. Specific actionable advice
3. Recommended next steps
4. Resources or opportunities to explore"""
    elif action == "job_search":
        preferences = payload.get("preferences", {})
        prompt = f"""Help user {user_id} with job search.
        
Request: {message}
Preferences: {preferences}

Provide:
1. Relevant job listings from database
2. External market opportunities
3. Application strategy recommendations
4. Company insights"""
    else:
        prompt = message or "Hello! How can I assist you with your career today?"

    response = agent(prompt)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
