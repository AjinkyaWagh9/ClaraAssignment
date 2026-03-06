"""
retell_client.py
Retell AI API integration.
Creates or updates agents via the Retell REST API.
Uses free tier account — create/update agents programmatically.

Docs: https://docs.retellai.com/api-references/create-agent
"""
import os, json, urllib.request, urllib.error
from pathlib import Path

RETELL_API_KEY = os.environ.get("RETELL_API_KEY", "")
BASE_URL = "https://api.retellai.com"

def _request(method: str, path: str, body: dict = None) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Retell API {method} {path} → {e.code}: {body}")

def create_agent(agent_spec: dict) -> dict:
    """
    Create a new Retell agent from an agent_spec dict.
    Returns the created agent object including agent_id.
    """
    if not RETELL_API_KEY:
        print("  [Retell] ⚠ RETELL_API_KEY not set — skipping API call, writing mock response")
        return _mock_create(agent_spec)

    payload = {
        "agent_name":    agent_spec["agent_name"],
        "voice_id":      agent_spec["voice_settings"]["voice_id"],
        "response_engine": {
            "type":   "retell-llm",
            "llm_id": _ensure_llm(agent_spec["system_prompt"]),
        },
    }
    result = _request("POST", "/create-agent", payload)
    print(f"  [Retell] ✓ Created agent: {result.get('agent_id')} ({agent_spec['agent_name']})")
    return result

def update_agent(agent_id: str, agent_spec: dict) -> dict:
    """Update an existing Retell agent to v2."""
    if not RETELL_API_KEY:
        print(f"  [Retell] ⚠ RETELL_API_KEY not set — skipping update for {agent_id}")
        return _mock_update(agent_id, agent_spec)

    payload = {
        "agent_name": agent_spec["agent_name"],
        "voice_id":   agent_spec["voice_settings"]["voice_id"],
    }
    result = _request("PATCH", f"/update-agent/{agent_id}", payload)
    print(f"  [Retell] ✓ Updated agent: {agent_id}")
    return result

def _ensure_llm(system_prompt: str) -> str:
    """Create a Retell LLM and return its llm_id."""
    payload = {
        "model": "gpt-4o",
        "general_prompt": system_prompt,
    }
    result = _request("POST", "/create-retell-llm", payload)
    return result.get("llm_id", "")

def _mock_create(agent_spec: dict) -> dict:
    """Return a mock Retell response when API key is missing."""
    import uuid
    return {
        "agent_id":   f"mock-{uuid.uuid4().hex[:8]}",
        "agent_name": agent_spec["agent_name"],
        "status":     "mock — set RETELL_API_KEY to create real agent",
        "manual_import_steps": agent_spec.get("retell_manual_import_steps", []),
    }

def _mock_update(agent_id: str, agent_spec: dict) -> dict:
    return {
        "agent_id": agent_id,
        "status":   "mock — set RETELL_API_KEY to update real agent",
    }
