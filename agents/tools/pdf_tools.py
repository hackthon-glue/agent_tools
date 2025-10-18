"""PDF parsing tools for resume analysis"""

import base64
import json
import boto3
from typing import Dict
from strands import tool
from .config import ToolConfig


@tool
def parse_resume_textract(pdf_base64: str) -> Dict:
    """Parse resume PDF using Textract for raw text extraction

    Args:
        pdf_base64: Base64 encoded PDF file

    Returns:
        Raw text and structured blocks from Textract
    """
    textract = boto3.client("textract", region_name=ToolConfig.AWS_REGION)
    pdf_bytes = base64.b64decode(pdf_base64)

    response = textract.analyze_document(
        Document={"Bytes": pdf_bytes}, FeatureTypes=["TABLES", "FORMS"]
    )

    text_blocks = []
    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
            text_blocks.append(block["Text"])

    return {"raw_text": "\n".join(text_blocks), "blocks": response["Blocks"]}


@tool
def parse_resume(pdf_base64: str, use_textract: bool = False) -> Dict:
    """Parse resume PDF and extract structured information

    Args:
        pdf_base64: Base64 encoded PDF file
        use_textract: If True, use Textract first then Claude for analysis

    Returns:
        Structured resume data with skills, experience, education
    """
    if use_textract:
        textract_result = parse_resume_textract(pdf_base64)
        raw_text = textract_result["raw_text"]

        bedrock = boto3.client("bedrock-runtime", region_name=ToolConfig.AWS_REGION)
        response = bedrock.invoke_model(
            modelId=ToolConfig.CLAUDE_MODEL_ID,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"""Extract structured information from this resume text:

{raw_text}

Return JSON with:
- name
- email
- phone
- skills (list)
- experience (list of {{company, role, duration, description}})
- education (list of {{school, degree, year}})
- summary""",
                        }
                    ],
                }
            ),
        )
        result = json.loads(response["body"].read())
        return json.loads(result["content"][0]["text"])

    bedrock = boto3.client("bedrock-runtime", region_name=ToolConfig.AWS_REGION)
    response = bedrock.invoke_model(
        modelId=ToolConfig.CLAUDE_MODEL_ID,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": """Extract structured information from this resume:

Return JSON with:
- name
- email  
- phone
- skills (list)
- experience (list of {company, role, duration, description})
- education (list of {school, degree, year})
- summary""",
                            },
                        ],
                    }
                ],
            }
        ),
    )
    result = json.loads(response["body"].read())
    return json.loads(result["content"][0]["text"])
