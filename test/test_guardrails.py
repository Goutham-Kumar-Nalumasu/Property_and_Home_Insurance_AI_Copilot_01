from app.guardrails import apply_response_guardrails, detect_unsafe_claim_language


def test_detect_unsafe_claim_language():
    text = "Your claim is approved and the insurer will definitely pay."
    violations = detect_unsafe_claim_language(text)

    assert "your claim is approved" in violations
    assert "the insurer will definitely pay" in violations


def test_apply_response_guardrails_adds_disclaimer():
    answer = "Based on the document, escape of water may be covered."
    guarded = apply_response_guardrails(answer)

    assert "Final claim outcomes" in guarded