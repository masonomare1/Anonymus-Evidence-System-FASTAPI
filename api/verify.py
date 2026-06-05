from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lib.handler import handle_verify

app = FastAPI()


@app.post("/")
async def verify(request: Request):
    body = await request.json()
    status_code, payload = handle_verify(body)
    return JSONResponse(content=payload, status_code=status_code)
