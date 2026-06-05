"""
Local dev server — serves static files AND runs POST /api/verify (mimics Vercel locally).

Run: python main.py
  (loads .env.local if present)

Then open http://localhost:3000
"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from lib.env import load_env
from lib.handler import handle_verify

load_env()

ROOT = Path(__file__).parent
app = FastAPI()


@app.post("/api/verify")
async def verify(request: Request):
    body = await request.json()
    status_code, payload = handle_verify(body)
    return JSONResponse(content=payload, status_code=status_code)


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")


if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", "3000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
