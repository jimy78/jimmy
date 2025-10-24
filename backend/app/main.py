from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="HR Agent Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: Request):
    payload = await req.json()
    # TODO: redact PII if REDACT_PII env is true, orchestrate OpenAI call
    message = payload.get("message") or payload.get("text") or ""
    # placeholder reply
    return {"reply": f"Prototype reply (echo): {message}"}

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"Echo: {data}")
    except Exception:
        await ws.close()