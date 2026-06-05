# Objection — Anonymous Source Verification (FastAPI)

Python/FastAPI port of the [Anonymus-Evidence-System](../Anonymus-Evidence-System) prototype. The HTML, CSS, and client JS are unchanged; only the backend is reimplemented in Python.

## Architecture

```
Browser (static, animated UI)                  Vercel serverless (Python)
 index.html   marketing page          POST      api/verify.py (FastAPI)
 verify.html  intake + results   ───────────▶   1. SHA-256 + timestamp + custody (per item)
 assets/app.js  flow state machine               2. transcribe audio (Groq Whisper)
 assets/ui.js   pipeline + certificate  ◀──────  3. analyze (Groq Llama, JSON mode)
 assets/style.css design system        verdict   4. validate (+1 repair retry) / fallback
                                          JSON    5. attach integrity, redact, return
```

| Module | Responsibility |
|---|---|
| `lib/integrity.py` | SHA-256 + custody entry |
| `lib/schema.py` | verdict schema validation, recursive redaction, safe fallback |
| `lib/prompt.py` | builds the consistency/corroboration/plausibility prompt |
| `lib/analyze.py` | orchestrator: transcribe → analyze → repair → integrity merge → redact |
| `lib/groq_client.py` | thin Groq adapters (`complete` = Llama JSON mode, `transcribe` = Whisper) |
| `lib/handler.py` | shared HTTP handler logic |
| `api/verify.py` | Vercel serverless FastAPI entry |
| `main.py` | local dev server (static files + `/api/verify`) |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env.local         # add your Groq key
python main.py                     # → http://localhost:3000
```

The bundled demo package (`evidence/demo.json`) works out of the box via **Load demo package**.

## Environment

| Variable | Where |
|---|---|
| `GROQ_API_KEY` | `.env.local` (local) or Vercel dashboard (production) |

---

_Prototype for the Objection "Project Silver" challenge. Not legal advice; reliability scores are AI-generated assessments, not adjudications._
