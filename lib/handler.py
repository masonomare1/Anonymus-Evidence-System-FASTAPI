import logging
import uuid
from datetime import datetime, timezone

from lib.analyze import analyze
from lib.groq_client import create_groq_client
from lib.schema import fallback_verdict

logger = logging.getLogger(__name__)


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _certificate_id():
    return "OBJ-2026-" + uuid.uuid4().hex[:6].upper()


def handle_verify(body):
    scenario_type = (body or {}).get("scenarioType", "Unknown")
    banned_terms = (body or {}).get("bannedTerms") or []
    items = (body or {}).get("items") or []

    if not isinstance(items, list) or len(items) == 0:
        return 400, {"error": "No evidence items submitted."}

    try:
        client = create_groq_client()
        verdict = analyze(
            {"scenarioType": scenario_type, "bannedTerms": banned_terms, "items": items},
            {
                "complete": client["complete"],
                "transcribe": client["transcribe"],
                "now": _now_iso,
                "id": _certificate_id,
            },
        )
        return 200, verdict
    except Exception as err:
        logger.exception("[verify] handler error: %s", err)
        fb = fallback_verdict(reason="server error")
        fb["certificateId"] = "OBJ-2026-ERROR"
        fb["issuedAt"] = _now_iso()
        return 200, fb
