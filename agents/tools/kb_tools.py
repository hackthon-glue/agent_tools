"""Knowledge Base tools for evaluation criteria"""

import boto3
from typing import List, Dict
from strands import tool
from .config import ToolConfig
from .base_tool import DataSourceTool


class KnowledgeBaseTool(DataSourceTool):
    """Knowledge Base access following SOLID principles"""

    def _create_client(self):
        return boto3.client("bedrock-agent-runtime", region_name=ToolConfig.AWS_REGION)

    def execute(self, query: str, kb_id: str = None, use_rerank: bool = None, 
                search_type: str = None, max_results: int = None) -> List[Dict]:
        try:
            return self._retrieve(
                query, 
                kb_id or ToolConfig.KB_ID, 
                use_rerank if use_rerank is not None else ToolConfig.KB_USE_RERANK,
                search_type or ToolConfig.KB_SEARCH_TYPE,
                max_results or ToolConfig.KB_MAX_RESULTS
            )
        except Exception as e:
            return self.handle_error(e, {"query": query, "kb_id": kb_id})

    def _retrieve(self, query: str, kb_id: str, use_rerank: bool, search_type: str, max_results: int) -> List[Dict]:
        config = {"vectorSearchConfiguration": {"numberOfResults": max_results}}
        if search_type == "HYBRID":
            config["vectorSearchConfiguration"]["overrideSearchType"] = "HYBRID"
        
        response = self.client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration=config
        )

        results = []
        for result in response.get("retrievalResults", []):
            results.append({
                "content": result["content"]["text"],
                "score": result["score"],
                "metadata": result.get("metadata", {})
            })
        
        if use_rerank and results:
            results = self._rerank(results, query, kb_id)
        return results
    
    def _rerank(self, results: List[Dict], query: str, kb_id: str) -> List[Dict]:
        response = self.client.rerank(
            knowledgeBaseId=kb_id,
            queries=[{"textQuery": {"text": query}, "type": "TEXT"}],
            sources=[{"inlineDocumentSource": {"textDocument": {"text": r["content"]}}, "type": "INLINE"} for r in results]
        )
        reranked = []
        for idx, result in enumerate(response.get("results", [])):
            original = results[result["index"]]
            original["rerank_score"] = result["relevanceScore"]
            reranked.append(original)
        return reranked
    
    def generate(self, query: str, kb_id: str = None, model_arn: str = None, 
                 temperature: float = None, max_tokens: int = None) -> Dict:
        temperature = temperature if temperature is not None else ToolConfig.KB_TEMPERATURE
        max_tokens = max_tokens or ToolConfig.KB_MAX_TOKENS
        response = self.client.retrieve_and_generate(
            input={"text": query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id or ToolConfig.KB_ID,
                    "modelArn": model_arn or f"arn:aws:bedrock:{ToolConfig.AWS_REGION}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": temperature,
                                "maxTokens": max_tokens
                            }
                        }
                    }
                }
            }
        )
        return {
            "output": response["output"]["text"],
            "citations": response.get("citations", []),
            "session_id": response.get("sessionId")
        }


_kb_tool = KnowledgeBaseTool()


@tool
def retrieve_evaluation_criteria(
    query: str, knowledge_base_id: str = None, use_rerank: bool = None,
    search_type: str = None, max_results: int = None
) -> List[Dict]:
    """Retrieve evaluation criteria from Knowledge Base

    Args:
        query: Search query for evaluation criteria
        knowledge_base_id: Knowledge Base ID (default: from .env)
        use_rerank: Enable reranking (default: from .env KB_USE_RERANK)
        search_type: "HYBRID" or "SEMANTIC" (default: from .env KB_SEARCH_TYPE)
        max_results: Maximum number of results (default: from .env KB_MAX_RESULTS)

    Returns:
        List of relevant evaluation criteria documents
    """
    return _kb_tool.execute(query, knowledge_base_id, use_rerank, search_type, max_results)


@tool
def generate_with_kb(
    query: str, knowledge_base_id: str = None, temperature: float = None, max_tokens: int = None
) -> Dict:
    """Generate response using Knowledge Base with RAG

    Args:
        query: Question or prompt
        knowledge_base_id: Knowledge Base ID (default: from .env)
        temperature: Response randomness 0-1 (default: from .env KB_TEMPERATURE)
        max_tokens: Maximum response length (default: from .env KB_MAX_TOKENS)

    Returns:
        Dict with output, citations, and session_id
    """
    return _kb_tool.generate(query, knowledge_base_id, None, temperature, max_tokens)
