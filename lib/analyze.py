import base64
import json

from lib.integrity import build_custody_entry, sha256
from lib.prompt import build_verification_prompt
from lib.schema import ITEM_RELIABILITY, fallback_verdict, redact, validate_verdict

MAX_AUDIO_BYTES = 4_000_000


def _try_parse(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _get_verdict(messages, complete):
    raw = complete(messages)
    parsed = _try_parse(raw)
    if parsed and len(validate_verdict(parsed)) == 0:
        return parsed

    repair = messages + [
        {
            "role": "system",
            "content": (
                "Your previous output was not valid JSON for the required schema. "
                "Return ONLY the corrected JSON object."
            ),
        }
    ]
    raw = complete(repair)
    parsed = _try_parse(raw)
    if parsed and len(validate_verdict(parsed)) == 0:
        return parsed
    return None


def analyze(input_data, deps):
    scenario_type = input_data.get("scenarioType", "Unknown")
    banned_terms = input_data.get("bannedTerms") or []
    items = input_data.get("items") or []
    complete = deps["complete"]
    transcribe = deps["transcribe"]
    now = deps["now"]
    cert_id = deps["id"]

    ingested_at = now()
    custody = {}

    for it in items:
        content = it.get("content") or ""
        hash_input = content
        if it.get("audioBase64"):
            audio_bytes = base64.b64decode(it["audioBase64"])
            hash_input = audio_bytes
            if not content:
                content = (
                    "[audio not transcribed: file exceeds size limit]"
                    if len(audio_bytes) > MAX_AUDIO_BYTES
                    else transcribe(audio_bytes)
                )
            it["content"] = content
        elif it.get("precomputedSha256"):
            hash_input = None

        hash_value = it.get("precomputedSha256") or sha256(hash_input if hash_input is not None else content)
        custody[it["label"]] = build_custody_entry(
            label=it["label"],
            type_=it["type"],
            hash_=hash_value,
            ingested_at=ingested_at,
        )

    messages = build_verification_prompt(
        scenario_type=scenario_type,
        items=items,
        banned_terms=banned_terms,
    )
    verdict = _get_verdict(messages, complete)
    if not verdict:
        verdict = fallback_verdict(
            reason="model returned invalid output",
            scenario_type=scenario_type,
        )

    model_rows = verdict.get("evidenceBreakdown") if isinstance(verdict.get("evidenceBreakdown"), list) else []
    verdict["certificateId"] = cert_id()
    verdict["issuedAt"] = ingested_at
    verdict["scenarioType"] = verdict.get("scenarioType") or scenario_type
    verdict["evidenceBreakdown"] = [
        {
            "label": it["label"],
            "type": it["type"],
            "integrity": custody.get(it["label"])
            or {"sha256": "", "ingestedAt": ingested_at, "status": "verified-from-intake"},
            "assessment": {
                "consistency": (model_rows[i].get("assessment") or {}).get("consistency", "Not assessed.")
                if i < len(model_rows)
                else "Not assessed.",
                "corroboration": (model_rows[i].get("assessment") or {}).get("corroboration", "Not assessed.")
                if i < len(model_rows)
                else "Not assessed.",
                "plausibility": (model_rows[i].get("assessment") or {}).get("plausibility", "Not assessed.")
                if i < len(model_rows)
                else "Not assessed.",
            },
            "reliability": model_rows[i].get("reliability")
            if i < len(model_rows) and model_rows[i].get("reliability") in ITEM_RELIABILITY
            else "Moderate",
        }
        for i, it in enumerate(items)
    ]

    return redact(verdict, banned_terms)
