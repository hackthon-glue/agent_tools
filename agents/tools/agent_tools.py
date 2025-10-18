"""Tools for calling specialized agents"""

from strands import tool
import importlib


@tool
def call_concierge(user_id: str, message: str, session_id: str = None) -> dict:
    """Call Concierge Agent for career consultation and job search

    Args:
        user_id: User ID
        message: User's message or question
        session_id: Optional session ID for conversation continuity

    Returns:
        Response from Concierge Agent
    """
    from concierge_agent import invoke

    return invoke(
        {"user_id": user_id, "message": message, "session_id": session_id or user_id}
    )


@tool
def call_skill_parser(user_id: str, resume_pdf: str = None) -> dict:
    """Call Skill Parser Agent to analyze resume and GitHub profile

    Args:
        user_id: User ID
        resume_pdf: Optional base64 encoded PDF resume

    Returns:
        Skill analysis results
    """
    from skill_parser_agent import invoke

    return invoke({"user_id": user_id, "resume_pdf": resume_pdf})


@tool
def call_job_matcher(user_id: str, filters: dict = None) -> dict:
    """Call Job Matcher Agent to find matching jobs

    Args:
        user_id: User ID
        filters: Optional filters (location, role, etc.)

    Returns:
        Job matching results with scores
    """
    from job_matcher_agent import invoke

    return invoke({"user_id": user_id, "filters": filters or {}})


@tool
def call_interviewer(
    user_id: str, interview_id: str, action: str, data: dict = None
) -> dict:
    """Call Interviewer Copilot Agent for interview support

    Args:
        user_id: User ID
        interview_id: Interview session ID
        action: Action to perform (generate_questions, evaluate, followup)
        data: Optional data (question, answer, etc.)

    Returns:
        Interview support response
    """
    from interviewer_copilot_agent import invoke

    return invoke(
        {
            "user_id": user_id,
            "interview_id": interview_id,
            "action": action,
            "data": data or {},
        }
    )
