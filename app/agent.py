import re
from typing import Dict, List, Tuple
from app.llm_client import generate_llm_answer
from app.guardrails import apply_response_guardrails
from app.mem0_manager import mem0_manager
from app.mcp_client import mcp_client
from app.schemas import Source
from app.tools.policy_compare import compare_policies   # fallback if MCP fails
from app.rag import rag_retriever                       # fallback

# Helper functions remain unchanged (detect_policy_type, detect_property_size, detect_claim_id, detect_intent, extract_damage_keywords)
def detect_policy_type(message: str) -> str | None:
    lower = message.lower()
    if "standard" in lower: return "Standard"
    if "comprehensive" in lower: return "Comprehensive"
    if "landlord" in lower: return "Landlord Plus"
    return None

def detect_property_size(message: str) -> str | None:
    patterns = ["1-bed flat/apartment", "2-bed terraced house", "3-bed semi-detached house", "3-bed detached house", "4-bed detached house", "5-bed+ large detached"]
    lower = message.lower()
    for p in patterns:
        if p.lower() in lower: return p
    if "3-bed semi" in lower: return "3-bed semi-detached house"
    if "2-bed terrace" in lower: return "2-bed terraced house"
    if "flat" in lower: return "1-bed flat/apartment"
    return None

def detect_claim_id(message: str) -> str | None:
    match = re.search(r"\bCLM[0-9A-Z]+\b", message.upper())
    return match.group(0) if match else None

def detect_intent(message: str) -> str:
    lower = message.lower()
    if "track claim" in lower or detect_claim_id(message): return "claim_status"
    if any(w in lower for w in ["estimate", "repair cost", "cost", "quote"]): return "damage_estimate"
    if "compare" in lower and "policy" in lower: return "policy_compare"
    if any(w in lower for w in ["remember", "i have", "my policy", "postcode", "property"]): return "memory_update"
    return "policy_rag"

def extract_damage_keywords(message: str) -> str:
    lower = message.lower()
    candidates = ["burst pipe","internal ceiling","water damage","roof tile","flat roof","fence","boundary wall","fire damage","smoke damage","flood damage","subsidence","theft","vandalism","accidental damage","kitchen","bathroom","carpet","door","window"]
    for cand in candidates:
        if cand in lower:
            return cand
    return message

def update_memory_from_message(session_id: str, message: str) -> Dict:
    updates = {}
    policy_type = detect_policy_type(message)
    property_size = detect_property_size(message)
    claim_id = detect_claim_id(message)
    if policy_type: updates["policy_type"] = policy_type
    if property_size: updates["property_size_category"] = property_size
    if claim_id: updates["claim_id"] = claim_id
    if "burst pipe" in message.lower():
        updates["damage_type"] = "burst pipe"
        updates["peril_category"] = "Water"
    if "storm" in message.lower():
        updates["peril_category"] = "Storm"
    if updates:
        return mem0_manager.update(session_id, updates)
    return mem0_manager.get(session_id)

def format_sources(results: List[Dict]) -> List[Source]:
    sources = []
    for r in results:
        sources.append(Source(
            document=r["document"],
            chunk_id=r["chunk_id"],
            score=round(r["score"],4),
            text_preview=r["text"][:250]+"..."
        ))
    return sources

def answer_policy_rag(message: str, memory: Dict) -> Tuple[str, List[Source]]:
    policy_type = memory.get("policy_type")
    # Call MCP tool
    try:
        result_text = mcp_client.call_tool("search_policy", {"query": message, "policy_type": policy_type})
    except Exception as e:
        # fallback to direct RAG
        results = rag_retriever.search(message, policy_type=policy_type)
        if not results:
            return "No indexed policy content found. Please run ingestion.", []
        context = "\n\n".join([f"Source: {r['document']}\n{r['text']}" for r in results])
        answer = generate_llm_answer(message, context, memory)
        return answer, format_sources(results)
    # If using MCP result, we lose structured sources; for simplicity, we reuse fallback for sources
    results = rag_retriever.search(message, policy_type=policy_type)
    return result_text, format_sources(results)

def answer_damage_estimate(message: str, memory: Dict) -> str:
    damage = extract_damage_keywords(message)
    prop_size = detect_property_size(message) or memory.get("property_size_category")
    peril = memory.get("peril_category")
    try:
        return mcp_client.call_tool("estimate_repair_cost", {
            "damage_type": damage,
            "property_size_category": prop_size,
            "peril_category": peril
        })
    except:
        # fallback to direct estimator
        from app.tools.damage_estimator import damage_estimator
        res = damage_estimator.estimate(damage, prop_size, peril)
        if not res["found"]:
            return res["message"]
        lines = [res["message"], ""]
        for m in res["matches"][:2]:
            lines.append(f"{m['damage_type']} | {m['property_size_category']}: £{m['repair_cost_low_gbp']} – £{m['repair_cost_high_gbp']}")
        return "\n".join(lines)

def run_agent(session_id: str, message: str) -> Dict:
    memory = update_memory_from_message(session_id, message)
    intent = detect_intent(message)
    memory = mem0_manager.update(session_id, {"last_user_intent": intent})
    sources = []

    if intent == "claim_status":
        claim_id = detect_claim_id(message) or memory.get("claim_id") or "UNKNOWN"
        try:
            answer = mcp_client.call_tool("get_claim_status", {"claim_id": claim_id})
        except:
            from app.tools.claim_status import get_claim_status
            status = get_claim_status(claim_id)
            answer = f"Claim {status.claim_id}: {status.status}. Next step: {status.next_step}"
    elif intent == "damage_estimate":
        answer = answer_damage_estimate(message, memory)
    elif intent == "policy_compare":
        try:
            answer = mcp_client.call_tool("compare_policy_tiers", {})
        except:
            summaries = compare_policies()
            answer = "Policy comparison:\n" + "\n".join([f"{k}: {v}" for k,v in summaries.items()])
    elif intent == "memory_update":
        policy_type = memory.get("policy_type")
        from app.tools.policy_compare import get_policy_summary
        summary = get_policy_summary(policy_type) if policy_type else {}
        answer = f"I have updated your session memory.\nCurrent memory: {memory}\n"
        if summary:
            answer += f"Summary for {policy_type}: {summary}"
    else:
        answer, sources = answer_policy_rag(message, memory)

    answer = apply_response_guardrails(answer)
    # Store conversation turn in Mem0 for recall
    mem0_manager.add_conversation_turn(session_id, message, answer)

    return {
        "session_id": session_id,
        "answer": answer,
        "intent": intent,
        "memory": mem0_manager.get(session_id),
        "sources": sources,
    }