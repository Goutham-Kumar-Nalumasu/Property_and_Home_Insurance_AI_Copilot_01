from typing import Dict


POLICY_SUMMARY = {
    "Standard": {
        "buildings_limit": "£300,000",
        "contents_limit": "£50,000",
        "buildings_excess": "£250",
        "contents_excess": "£150",
        "accidental_damage": "Not included as standard; available as add-on",
        "legal_expenses": "Not included as standard; available as add-on",
        "home_emergency": "Not included as standard; available as add-on",
    },
    "Comprehensive": {
        "buildings_limit": "£500,000",
        "contents_limit": "£100,000",
        "buildings_excess": "£150",
        "contents_excess": "£100",
        "accidental_damage": "Included",
        "legal_expenses": "Included up to £50,000",
        "home_emergency": "Included",
    },
    "Landlord Plus": {
        "buildings_limit": "£750,000",
        "contents_limit": "£30,000 for furnished lets",
        "buildings_excess": "£250",
        "contents_excess": "£200",
        "accidental_damage": "Selected landlord cover; tenant malicious damage included up to £25,000",
        "legal_expenses": "Included up to £100,000",
        "home_emergency": "Depends on selected cover and schedule",
    },
}


def compare_policies() -> Dict:
    return POLICY_SUMMARY


def get_policy_summary(policy_type: str) -> Dict:
    for key, value in POLICY_SUMMARY.items():
        if key.lower() == policy_type.lower():
            return value

    return {}