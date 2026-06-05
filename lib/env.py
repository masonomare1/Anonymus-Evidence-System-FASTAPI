import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_loaded = False


def load_env():
    global _loaded
    if _loaded:
        return
    try:
        from dotenv import load_dotenv

        for path in (ROOT / ".env.local", ROOT / ".env", ROOT.parent / ".env.local"):
            if path.is_file():
                load_dotenv(path)
    except ImportError:
        pass
    _loaded = True


def get_groq_api_key():
    load_env()
    return (os.environ.get("GROQ_API_KEY") or "").strip()
