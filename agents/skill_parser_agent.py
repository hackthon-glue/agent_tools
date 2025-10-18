"""Skill Parser Agent - Resume and GitHub profile analysis"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools.pdf_tools import parse_resume
from tools.dynamodb_tools import get_github_profile
from tools.collector_tools import search_github_profile, search_linkedin_profile
from tools.config import ToolConfig
from memory_hook import MemoryHook

app = BedrockAgentCoreApp()

agent = Agent(
    model=ToolConfig.CLAUDE_MODEL_ID,
    system_prompt="""You are a technical skill analyzer that:
    
    **Resume Analysis:**
    - Extract technical skills with proficiency levels
    - Identify experience domains and years
    - Evaluate project complexity and impact
    
    **GitHub Profile Analysis:**
    - Analyze programming languages and usage patterns
    - Evaluate repository quality and contributions
    - Identify technical expertise areas
    - Assess code quality and best practices
    
    **Skill Extraction:**
    - Parse technical skills from any text
    - Categorize skills (languages, frameworks, tools, methodologies)
    - Rate proficiency based on context
    
    **Output Format:**
    Return structured JSON with:
    - technical_skills: [{skill, category, proficiency_level}]
    - experience_summary: {years, domains, seniority}
    - github_analysis: {languages, notable_projects, contribution_pattern}
    - overall_rating: 1-10 scale with justification
    
    Use parse_resume for PDF analysis.
    Use get_github_profile for GitHub data from DynamoDB.
    Use search_github_profile to search GitHub profiles online.
    Use search_linkedin_profile to gather professional background.""",
    tools=[
        parse_resume,
        get_github_profile,
        search_github_profile,
        search_linkedin_profile,
    ],
    hooks=[MemoryHook()] if ToolConfig.MEMORY_ID else [],
    state={"session_id": "default"},
)


@app.entrypoint
def invoke(payload, context):
    """Parse skills from resume and GitHub"""
    if hasattr(context, "session_id"):
        agent.state.set("session_id", context.session_id)

    action = payload.get("action", "full_analysis")
    user_id = payload.get("user_id")

    if action == "parse_resume":
        pdf_base64 = payload.get("resume_pdf")
        prompt = f"""Parse resume for user {user_id}.

Extract:
1. Technical skills with proficiency indicators
2. Work experience (years, roles, companies)
3. Education and certifications
4. Notable projects and achievements

Return structured JSON format."""

    elif action == "parse_github":
        github_url = payload.get("github_url", "")
        prompt = f"""Analyze GitHub profile: {github_url}

Evaluate:
1. Programming languages and usage percentage
2. Repository quality (stars, forks, activity)
3. Contribution patterns (frequency, consistency)
4. Code quality indicators
5. Notable projects with impact assessment

Return detailed technical profile."""

    elif action == "extract_skills":
        text = payload.get("text", "")
        source_type = payload.get("source_type", "general")
        prompt = f"""Extract technical skills from text (source: {source_type}).

Text: {text}

Identify:
1. Programming languages
2. Frameworks and libraries
3. Tools and platforms
4. Methodologies and practices
5. Proficiency level indicators

Categorize and rate each skill."""

    else:  # full_analysis
        prompt = f"""Comprehensive skill analysis for user {user_id}.

Steps:
1. Get user profile from database
2. Parse resume if available
3. Analyze GitHub profile
4. Search LinkedIn for additional context
5. Create unified skill assessment

Return complete technical profile with ratings."""

    response = agent(prompt)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
