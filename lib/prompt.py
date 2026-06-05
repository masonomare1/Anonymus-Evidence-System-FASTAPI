from lib.schema import RELIABILITY

MAX_ITEM_CHARS = 8000


def _clip(content):
    s = content or ""
    if len(s) > MAX_ITEM_CHARS:
        return s[:MAX_ITEM_CHARS] + "\n…[content truncated to fit token budget]"
    return s


def build_verification_prompt(*, scenario_type, items, banned_terms=None):
    banned_terms = banned_terms or []
    system_parts = [
        "You are Objection's evidence verification engine — 'The AI Tribunal of Truth'.",
        "Assess a package of evidence submitted by an ANONYMOUS source and return ONLY a JSON object.",
        "For every item AND across the package, evaluate three dimensions:",
        "- consistency: does each item agree with itself and the others (dates, names, numbers, claims)?",
        '- corroboration: which OTHER items support each claim? Cite them by label (e.g. "Corroborated by Evidence B").',
        "- plausibility: does this read like genuine evidence rather than fabrication?",
        f"Then classify overall reliability as one of: {', '.join(RELIABILITY)}, with a confidenceScore 0-100.",
        'PRIVACY: refer to people only by role ("the source", "the accused", "the corroborating witness").',
    ]
    if banned_terms:
        system_parts.append(
            f"NEVER output these names or identifying terms: {', '.join(banned_terms)}."
        )
    system_parts.extend(
        [
            "Do NOT invent hashes, ids, or timestamps — the system computes integrity fields; omit them.",
            "Return JSON with keys: scenarioType, overallReliability, confidenceScore, summary,",
            "evidenceBreakdown[] (label, type, assessment{consistency,corroboration,plausibility}, reliability),",
            "crossEvidence{consistency,corroboration,plausibility,contradictions[]},",
            "attribution{short,extended}, limitations[].",
            'attribution.short MUST be copy-paste ready, e.g. "...said a source verified via Objection\'s independent certification process."',
        ]
    )
    system = "\n".join(system_parts)

    evidence = "\n\n".join(
        f"### {it['label']} ({it['type']})\n{_clip(it.get('content'))}" for it in items
    )
    user = f"Scenario: {scenario_type}\n\nEvidence package:\n\n{evidence}\n\nReturn the JSON verdict now."

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
