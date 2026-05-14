from typing import List


BLOCKED_FINAL_DECISION_PHRASES = [
    "your claim is approved",
    "your claim has been approved",
    "the insurer will definitely pay",
    "guaranteed payout",
    "we guarantee",
    "legally binding advice",
]


def detect_unsafe_claim_language(text: str) -> List[str]:
    lower_text = text.lower()
    violations = []

    for phrase in BLOCKED_FINAL_DECISION_PHRASES:
        if phrase in lower_text:
            violations.append(phrase)

    return violations


def apply_response_guardrails(answer: str) -> str:
    violations = detect_unsafe_claim_language(answer)

    if violations:
        answer = (
            "I can provide general information from the HomeShield documents, "
            "but I cannot approve claims, guarantee payouts, or provide binding legal advice. "
            "Final decisions depend on insurer assessment.\n\n"
            + answer
        )

    required_disclaimer = (
        "\n\nNote: This is informational guidance based on the uploaded HomeShield "
        "training documents. Final claim outcomes depend on policy schedule, evidence, "
        "insurer assessment, and applicable terms."
    )

    if "Final claim outcomes" not in answer:
        answer += required_disclaimer

    return answer