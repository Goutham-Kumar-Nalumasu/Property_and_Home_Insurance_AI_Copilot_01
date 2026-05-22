import re
from typing import Dict, List, Tuple
from app.llm_client import generate_llm_answer
from app.guardrails import apply_response_guardrails
from app.memory import memory_manager
from app.rag import rag_retriever
from app.schemas import Source
from app.tools.claim_status import get_claim_status
from app.tools.damage_estimator import damage_estimator
from app.tools.policy_compare import compare_policies, get_policy_summary


def detect_policy_type(message: str) -> str | None:
    lower = message.lower()

    if "standard" in lower:
        return "Standard"
    if "comprehensive" in lower:
        return "Comprehensive"
    if "landlord" in lower:
        return "Landlord Plus"

    return None


def detect_property_size(message: str) -> str | None:
    patterns = [
        "1-bed flat/apartment",
        "2-bed terraced house",
        "3-bed semi-detached house",
        "3-bed detached house",
        "4-bed detached house",
        "5-bed+ large detached",
    ]

    lower = message.lower()

    for pattern in patterns:
        if pattern.lower() in lower:
            return pattern

    if "3-bed semi" in lower:
        return "3-bed semi-detached house"
    if "2-bed terrace" in lower:
        return "2-bed terraced house"
    if "flat" in lower:
        return "1-bed flat/apartment"

    return None


def detect_claim_id(message: str) -> str | None:
    match = re.search(r"\bCLM[0-9A-Z]+\b", message.upper())
    return match.group(0) if match else None


def detect_intent(message: str) -> str:
    lower = message.lower()

    if "track claim" in lower or detect_claim_id(message):
        return "claim_status"

    if any(word in lower for word in ["estimate", "repair cost", "cost", "quote"]):
        return "damage_estimate"

    if "compare" in lower and "policy" in lower:
        return "policy_compare"

    if any(word in lower for word in ["remember", "i have", "my policy", "postcode", "property"]):
        return "memory_update"

    return "policy_rag"


def extract_damage_keywords(message: str) -> str:
    lower = message.lower()

    candidates = [
        "burst pipe",
        "internal ceiling",
        "water damage",
        "roof tile",
        "flat roof",
        "fence",
        "boundary wall",
        "fire damage",
        "smoke damage",
        "flood damage",
        "subsidence",
        "theft",
        "vandalism",
        "accidental damage",
        "kitchen",
        "bathroom",
        "carpet",
        "door",
        "window",
    ]

    found = [candidate for candidate in candidates if candidate in lower]

    if found:
        return found[0]

    return message


def update_memory_from_message(session_id: str, message: str) -> Dict:
    updates = {}

    policy_type = detect_policy_type(message)
    property_size = detect_property_size(message)
    claim_id = detect_claim_id(message)

    if policy_type:
        updates["policy_type"] = policy_type

    if property_size:
        updates["property_size_category"] = property_size

    if claim_id:
        updates["claim_id"] = claim_id

    if "burst pipe" in message.lower():
        updates["damage_type"] = "burst pipe"
        updates["peril_category"] = "Water"

    if "storm" in message.lower():
        updates["peril_category"] = "Storm"

    if updates:
        return memory_manager.update(session_id, updates)

    return memory_manager.get(session_id)




def format_sources(results: List[Dict]) -> List[Source]:
    sources = []

    for result in results:
        sources.append(
            Source(
                document=result["document"],
                chunk_id=result["chunk_id"],
                score=round(result["score"], 4),
                text_preview=result["text"][:250] + "...",
            )
        )

    return sources


"""
def answer_policy_rag(message: str, memory: Dict) -> Tuple[str, List[Source]]:
    policy_type = memory.get("policy_type")
    results = rag_retriever.search(message, policy_type=policy_type)

    if not results:
        answer = (
            "I could not find indexed policy content. Please run "
            "`python -m app.document_loader` and try again."
        )
        return answer, []

    context = "\n\n".join(
        [
            f"Source: {item['document']} | Chunk {item['chunk_id']}\n{item['text']}"
            for item in results
        ]
    )

    answer = (
        "Based on the uploaded HomeShield documents, here is the most relevant information:\n\n"
        f"{context[:1800]}\n\n"
        "Please review the cited source chunks above. If you want, ask a more specific question "
        "such as coverage limit, excess, exclusion, or claim scenario."
    )

    return answer, format_sources(results)
"""

def answer_policy_rag(message: str, memory: Dict) -> Tuple[str, List[Source]]:
    policy_type = memory.get("policy_type")
    results = rag_retriever.search(message, policy_type=policy_type)

    if not results:
        answer = (
            "I could not find indexed policy content. Please run "
            "`python -m app.document_loader` or call `/ingest` and try again."
        )
        return answer, []

    context = "\n\n".join(
        [
            f"Source document: {item['document']} | Chunk: {item['chunk_id']}\n"
            f"{item['text']}"
            for item in results
        ]
    )

    answer = generate_llm_answer(
        question=message,
        context=context,
        memory=memory,
    )

    return answer, format_sources(results)


def answer_damage_estimate(message: str, memory: Dict) -> str:
    damage_keyword = extract_damage_keywords(message)

    property_size = (
        detect_property_size(message)
        or memory.get("property_size_category")
    )

    peril = memory.get("peril_category")

    result = damage_estimator.estimate(
        damage_type=damage_keyword,
        property_size_category=property_size,
        peril_category=peril,
    )

    if not result["found"]:
        return result["message"]

    lines = [result["message"], ""]

    for match in result["matches"]:
        lines.append(f"Damage type: {match.get('damage_type')}")
        lines.append(f"Peril category: {match.get('peril_category')}")
        lines.append(f"Component: {match.get('affected_component')}")
        lines.append(f"Property size: {match.get('property_size_category')}")
        lines.append(
            "Estimated cost: "
            f"£{match.get('repair_cost_low_gbp')} - £{match.get('repair_cost_high_gbp')} "
            f"(average £{match.get('repair_cost_avg_gbp')})"
        )
        lines.append(f"Typical labour days: {match.get('typical_labour_days')}")
        lines.append(f"VAT included: {match.get('vat_included')}")
        lines.append(f"Recommended quotes: {match.get('recommended_quotes')}")
        lines.append(f"Specialist required: {match.get('specialist_required')}")
        if match.get("notes"):
            lines.append(f"Notes: {match.get('notes')}")
        lines.append("")

    lines.append(
        "This is an indicative repair-cost estimate only and is not a claim approval or settlement offer."
    )

    return "\n".join(lines)


def run_agent(session_id: str, message: str) -> Dict:
    memory = update_memory_from_message(session_id, message)
    intent = detect_intent(message)

    memory = memory_manager.update(session_id, {"last_user_intent": intent})

    sources: List[Source] = []

    if intent == "claim_status":
        claim_id = detect_claim_id(message) or memory.get("claim_id") or "UNKNOWN"
        status = get_claim_status(claim_id)
        answer = (
            f"Claim ID: {status.claim_id}\n"
            f"Current simulated status: {status.status}\n"
            f"Next step: {status.next_step}\n\n"
            "This is a simulated capstone claim tracker, not a real insurer system."
        )

    elif intent == "damage_estimate":
        answer = answer_damage_estimate(message, memory)

    elif intent == "policy_compare":
        summaries = compare_policies()
        answer = "Policy comparison summary:\n\n"
        for policy, details in summaries.items():
            answer += f"{policy}:\n"
            for key, value in details.items():
                answer += f"- {key.replace('_', ' ').title()}: {value}\n"
            answer += "\n"

    elif intent == "memory_update":
        policy_type = memory.get("policy_type")
        summary = get_policy_summary(policy_type) if policy_type else {}

        answer = "I have updated your session memory.\n\n"
        answer += f"Current memory: {memory}\n\n"

        if summary:
            answer += f"Known summary for {policy_type}:\n"
            for key, value in summary.items():
                answer += f"- {key.replace('_', ' ').title()}: {value}\n"

    else:
        answer, sources = answer_policy_rag(message, memory)

    answer = apply_response_guardrails(answer)

    return {
        "session_id": session_id,
        "answer": answer,
        "intent": intent,
        "memory": memory_manager.get(session_id),
        "sources": sources,
    }