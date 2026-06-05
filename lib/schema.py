import re

RELIABILITY = ["High", "Moderate", "Low", "Insufficient"]
ITEM_RELIABILITY = ["High", "Moderate", "Low"]
EVIDENCE_TYPES = [
    "intake_notes",
    "correspondence",
    "audio",
    "data_analysis",
    "personal_notes",
]


def _is_str(x):
    return isinstance(x, str) and len(x) > 0


def validate_verdict(v):
    errors = []
    if not v or not isinstance(v, dict):
        return ["verdict is not an object"]
    if v.get("overallReliability") not in RELIABILITY:
        errors.append(f"overallReliability invalid: {v.get('overallReliability')}")
    score = v.get("confidenceScore")
    if not isinstance(score, (int, float)) or score < 0 or score > 100:
        errors.append(f"confidenceScore out of range: {score}")
    if not _is_str(v.get("summary")):
        errors.append("summary missing")
    breakdown = v.get("evidenceBreakdown")
    if not isinstance(breakdown, list) or len(breakdown) == 0:
        errors.append("evidenceBreakdown empty")
    else:
        for i, it in enumerate(breakdown):
            if not _is_str(it.get("label")):
                errors.append(f"evidenceBreakdown[{i}].label missing")
            assessment = it.get("assessment") or {}
            if (
                not _is_str(assessment.get("consistency"))
                or not _is_str(assessment.get("corroboration"))
                or not _is_str(assessment.get("plausibility"))
            ):
                errors.append(f"evidenceBreakdown[{i}].assessment incomplete")
            if it.get("reliability") not in ITEM_RELIABILITY:
                errors.append(f"evidenceBreakdown[{i}].reliability invalid")
    cross = v.get("crossEvidence") or {}
    if (
        not _is_str(cross.get("consistency"))
        or not _is_str(cross.get("corroboration"))
        or not _is_str(cross.get("plausibility"))
    ):
        errors.append("crossEvidence incomplete")
    attribution = v.get("attribution") or {}
    if not _is_str(attribution.get("short")) or not _is_str(attribution.get("extended")):
        errors.append("attribution incomplete")
    limitations = v.get("limitations")
    if not isinstance(limitations, list) or len(limitations) == 0:
        errors.append("limitations empty")
    return errors


def _redact_string(s, terms):
    out = s
    for term in terms:
        if not term:
            continue
        pattern = re.escape(term)
        out = re.sub(pattern, "[redacted]", out, flags=re.IGNORECASE)
    return out


def redact(value, terms=None):
    terms = terms or []
    if not terms:
        return value
    if isinstance(value, str):
        return _redact_string(value, terms)
    if isinstance(value, list):
        return [redact(x, terms) for x in value]
    if isinstance(value, dict):
        return {k: redact(v, terms) for k, v in value.items()}
    return value


def fallback_verdict(*, reason="analysis unavailable", scenario_type="Unknown"):
    return {
        "certificateId": "",
        "issuedAt": "",
        "scenarioType": scenario_type,
        "overallReliability": "Insufficient",
        "confidenceScore": 0,
        "summary": (
            f"Automated verification could not be completed ({reason}). "
            "No reliability claim is made."
        ),
        "evidenceBreakdown": [
            {
                "label": "Evidence",
                "type": "intake_notes",
                "integrity": {
                    "sha256": "",
                    "ingestedAt": "",
                    "status": "verified-from-intake",
                },
                "assessment": {
                    "consistency": "Not assessed.",
                    "corroboration": "Not assessed.",
                    "plausibility": "Not assessed.",
                },
                "reliability": "Low",
            }
        ],
        "crossEvidence": {
            "consistency": "Not assessed.",
            "corroboration": "Not assessed.",
            "plausibility": "Not assessed.",
            "contradictions": [],
        },
        "attribution": {
            "short": "Verification could not be completed for this submission.",
            "extended": (
                "Objection was unable to complete automated verification for this "
                "submission; no reliability determination was made."
            ),
        },
        "limitations": [
            "Does not verify the real-world identity of the anonymous source.",
            "Establishes integrity from the point of intake, not cryptographic origin.",
        ],
    }
