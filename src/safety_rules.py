"""
Rule-based safety/severity layer.

Safety hazards always force Critical priority.

Certain hazards also force the correct category so that
the ML classifier cannot route a dangerous electrical complaint
to an unrelated department such as Cleaning.
"""

from typing import List, Tuple

from config import CRITICAL_KEYWORDS


# Keywords that specifically indicate an electrical hazard.
# These override the ML category because safety-critical
# complaints must be routed to the appropriate team.
ELECTRICAL_HAZARD_KEYWORDS = [
    "electric shock",
    "electrical shock",
    "shock",
    "electrocuted",
    "electrocution",
    "electricity shock",
    "live wire",
    "exposed wire",
    "exposed live wire",
    "sparking",
    "sparks",
    "spark",
]


def apply_safety_rules(
    raw_text: str,
    ml_priority: str
) -> Tuple[str, bool, List[str]]:
    """
    Returns:
        (final_priority, was_escalated, matched_keywords)

    Any critical safety keyword forces Critical priority.
    """

    text_lower = str(raw_text).lower()

    matched = [
        kw for kw in CRITICAL_KEYWORDS
        if kw in text_lower
    ]

    if matched:
        return "Critical", True, matched

    return ml_priority, False, []


def get_safety_category(raw_text: str):
    """
    Returns a category override for safety-critical complaints.

    Currently:
        Electrical hazards -> Electrical

    Returns:
        "Electrical" or None
    """

    text_lower = str(raw_text).lower()

    electrical_matches = [
        kw
        for kw in ELECTRICAL_HAZARD_KEYWORDS
        if kw in text_lower
    ]

    if electrical_matches:
        return "Electrical"

    return None