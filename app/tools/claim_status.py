import hashlib
from app.schemas import ClaimStatusResponse


STATUSES = [
    {
        "status": "Registered",
        "next_step": "Claims team will review initial details and may request photos or invoices.",
    },
    {
        "status": "Evidence Requested",
        "next_step": "Please upload photos, repair quotes, receipts, or incident reports.",
    },
    {
        "status": "Assessment In Progress",
        "next_step": "A claims handler or surveyor is reviewing the damage and policy terms.",
    },
    {
        "status": "Awaiting Contractor Quote",
        "next_step": "Please arrange or submit the requested contractor quote.",
    },
    {
        "status": "Decision Pending",
        "next_step": "The insurer will confirm the outcome after final review.",
    },
]


def get_claim_status(claim_id: str) -> ClaimStatusResponse:
    """
    Simulates claim status using deterministic hashing.
    This does not connect to a real claims system.
    """

    normalized = claim_id.strip().upper()

    if not normalized:
        normalized = "UNKNOWN"

    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(STATUSES)

    selected = STATUSES[index]

    return ClaimStatusResponse(
        claim_id=normalized,
        status=selected["status"],
        next_step=selected["next_step"],
    )