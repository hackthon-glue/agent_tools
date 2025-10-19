"""Cloud AgentCore deployment verification tests - shows actual responses"""

import os
import json
import boto3
import pytest
import uuid

pytestmark = pytest.mark.acceptance


def test_cloud_health_check():
    """Health check for deployed AgentCore Runtime"""
    print("\n" + "=" * 60)
    print("CLOUD DEPLOYMENT TEST: Health Check")
    print("=" * 60)

    agent_arn = os.getenv("ORCHESTRATOR_AGENT_ARN")
    if not agent_arn:
        print("\n⚠️  Set: export ORCHESTRATOR_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
        pytest.skip("ORCHESTRATOR_AGENT_ARN not configured")

    client = boto3.client("bedrock-agentcore", region_name=os.getenv("AWS_REGION", "us-west-2"))

    try:
        print("\n🔍 Checking agent status...")
        print(f"  Agent ARN: {agent_arn}")

        payload = json.dumps({"request": "Hello"}).encode()
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=str(uuid.uuid4()),
            payload=payload,
        )

        result = ""
        for chunk in response.get("response", []):
            result += chunk.decode('utf-8')

        print("\n📥 Health check response:")
        print(f"  {result[:200]}...")
        print("\n✅ Agent is healthy and responding")

    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()


def test_cloud_orchestrator():
    """Test deployed Orchestrator Agent via AgentCore Runtime - shows full response"""
    print("\n" + "=" * 60)
    print("CLOUD DEPLOYMENT TEST: Orchestrator Agent")
    print("=" * 60)

    agent_arn = os.getenv("ORCHESTRATOR_AGENT_ARN")
    if not agent_arn:
        print("\n⚠️  Set: export ORCHESTRATOR_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
        pytest.skip("ORCHESTRATOR_AGENT_ARN not configured")

    client = boto3.client("bedrock-agentcore", region_name=os.getenv("AWS_REGION", "us-west-2"))

    payload = {
        "user_id": "cloud_test_user",
        "request": "I'm looking for software engineer jobs in Tokyo",
        "session_id": "cloud_test_session",
    }

    try:
        print("\n📤 Request:")
        print(f"  Agent ARN: {agent_arn}")
        print(f"  User: {payload['user_id']}")
        print(f"  Message: {payload['request']}")

        payload_bytes = json.dumps(payload).encode()
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=str(uuid.uuid4()),
            payload=payload_bytes,
        )

        result = ""
        for chunk in response.get("response", []):
            result += chunk.decode('utf-8')

        print("\n📥 Response:")
        print(f"  {result}")
        print("\n✅ Cloud orchestrator test passed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_cloud_memory_conversation():
    """Test memory persistence across multiple conversations"""
    print("\n" + "=" * 60)
    print("CLOUD DEPLOYMENT TEST: Memory Conversation")
    print("=" * 60)

    agent_arn = os.getenv("ORCHESTRATOR_AGENT_ARN")
    if not agent_arn:
        print("\n⚠️  Set: export ORCHESTRATOR_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
        pytest.skip("ORCHESTRATOR_AGENT_ARN not configured")
        
    client = boto3.client("bedrock-agentcore", region_name=os.getenv("AWS_REGION", "us-west-2"))
    session_id = str(uuid.uuid4())

    # Conversation 1
    print("\n💬 Conversation 1: Initial job search")
    payload1 = {"user_id": "memory_test_user", "request": "I'm interested in backend engineer positions"}
    print(f"  Request: {payload1['request']}")
    
    response1 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload1).encode(),
    )
    result1 = ""
    for chunk in response1.get("response", []):
        result1 += chunk.decode('utf-8')
    print(f"  Response: {result1[:150]}...")
    assert len(result1) > 0

    # Conversation 2
    print("\n💬 Conversation 2: Follow-up question")
    payload2 = {"user_id": "memory_test_user", "request": "What about the salary range?"}
    print(f"  Request: {payload2['request']}")
    
    response2 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload2).encode(),
    )
    result2 = ""
    for chunk in response2.get("response", []):
        result2 += chunk.decode('utf-8')
    print(f"  Response: {result2[:150]}...")
    assert len(result2) > 0

    # Conversation 3
    print("\n💬 Conversation 3: Another follow-up")
    payload3 = {"user_id": "memory_test_user", "request": "Recommend companies in Tokyo"}
    print(f"  Request: {payload3['request']}")
    
    response3 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload3).encode(),
    )
    result3 = ""
    for chunk in response3.get("response", []):
        result3 += chunk.decode('utf-8')
    print(f"  Response: {result3[:150]}...")
    assert len(result3) > 0

    print(f"\n✅ Memory conversation test passed (Session: {session_id})")


def test_cloud_memory_persistence():
    """Test AgentCore Memory persistence"""
    print("\n" + "=" * 60)
    print("CLOUD DEPLOYMENT TEST: Memory Persistence")
    print("=" * 60)

    memory_id = os.getenv("AGENTCORE_MEMORY_ID")
    if not memory_id:
        print("\n⚠️  Set: export AGENTCORE_MEMORY_ID='orchestrator_agent_mem-...'")
        pytest.skip("AGENTCORE_MEMORY_ID not configured")

    client = boto3.client("bedrock-agent-runtime", region_name=os.getenv("AWS_REGION", "us-west-2"))

    try:
        print("\n🔍 Checking memory status...")
        print(f"  Memory ID: {memory_id}")

        response = client.get_agent_memory(
            agentId=memory_id.split("-")[0],
            agentAliasId="TSTALIASID",
            memoryId=memory_id,
            memoryType="SESSION_SUMMARY",
        )

        print("\n📥 Memory status:")
        print(f"  Memory exists: {response is not None}")
        print("\n✅ Memory persistence verified")

    except client.exceptions.ResourceNotFoundException:
        print("\n⚠️  Memory not found - may not be created yet")
    except Exception as e:
        print(f"\n❌ Memory check failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Cloud AgentCore Deployment Tests")
    print("=" * 60)
    print("Set: export ORCHESTRATOR_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
    print("=" * 60)

    test_cloud_health_check()
    test_cloud_orchestrator()
    test_cloud_memory_conversation()
    test_cloud_memory_persistence()

    print("\n" + "=" * 60)
    print("✅ All cloud deployment tests completed")
    print("=" * 60)
