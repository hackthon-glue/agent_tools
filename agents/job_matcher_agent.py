"""Job Matcher Agent - Match candidates with optimal job positions"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools.dynamodb_tools import get_user_profile, get_job_listings
from tools.kb_tools import retrieve_evaluation_criteria
from tools.config import ToolConfig
from memory_hook import MemoryHook

app = BedrockAgentCoreApp()

agent = Agent(
    model=ToolConfig.CLAUDE_MODEL_ID,
    system_prompt="""You are a job matching specialist that:
    
    **Matching Evaluation:**
    - Skills Match (0-100%): Technical and soft skills alignment
    - Experience Match (0-100%): Years and domain relevance
    - Culture Fit (0-100%): Values and work style compatibility
    - Growth Potential (0-100%): Learning and advancement opportunities
    
    **Scoring Methodology:**
    - Required skills: Must have 80%+ match
    - Preferred skills: Bonus points for each match
    - Experience level: ±2 years acceptable
    - Location/Remote: Strict or flexible based on job
    
    **Output Format:**
    For each match provide:
    1. Overall score (0-100)
    2. Breakdown by category
    3. Strengths (why good fit)
    4. Concerns (potential issues)
    5. Recommendations (how to improve fit)
    
    Use get_user_profile to get candidate data from DynamoDB.
    Use get_job_listings to get available positions from DynamoDB.
    Use retrieve_evaluation_criteria to get matching criteria from KB.""",
    tools=[get_user_profile, get_job_listings, retrieve_evaluation_criteria],
    hooks=[MemoryHook()] if ToolConfig.MEMORY_ID else [],
    state={"session_id": "default"},
)


@app.entrypoint
def invoke(payload, context):
    """Match candidate with jobs"""
    if hasattr(context, "session_id"):
        agent.state.set("session_id", context.session_id)

    action = payload.get("action", "match_jobs")
    user_id = payload.get("user_id")

    if action == "match_jobs":
        filters = payload.get("filters", {})
        prompt = f"""Match candidate {user_id} with available jobs.

Filters: {filters}

Steps:
1. Get candidate profile from database
2. Get job listings matching filters
3. Retrieve evaluation criteria from Knowledge Base
4. Calculate match scores for each job

Return top 5 matches with:
- job_id, title, company
- overall_score (0-100)
- skills_match, experience_match, culture_fit (each 0-100)
- strengths (3-5 points)
- concerns (if any)
- recommendation (apply/consider/skip)"""

    elif action == "evaluate_fit":
        job_id = payload.get("job_id")
        detailed = payload.get("detailed_analysis", False)
        prompt = f"""Detailed fit evaluation for candidate {user_id} and job {job_id}.

Analyze:
1. Required skills fulfillment (must-haves)
2. Preferred skills fulfillment (nice-to-haves)
3. Experience level alignment
4. Culture fit indicators
5. Growth potential
6. Risk factors

{"Provide comprehensive analysis report with recommendations." if detailed else "Provide concise evaluation summary."}

Include:
- Fit score (0-100) with breakdown
- Interview focus areas
- Onboarding considerations
- Success probability (low/medium/high)"""

    else:
        prompt = f"Find best job matches for user {user_id}"

    response = agent(prompt)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
