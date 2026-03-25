from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import json
import logging
import anthropic

# Basic logger
logger = logging.getLogger("hr-agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Read env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
REDACT_PII = os.getenv("REDACT_PII", "true").lower() in ("1", "true", "yes")

if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY is not set. Claude calls will fail until it is configured.")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

app = FastAPI(title="HR Agent - Claude")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = (
    "Vous etes un assistant RH expert. Repondez de maniere concise, professionnelle et conforme au RGPD. "
    "Si la requete contient des informations personnelles identifiables, appliquez les regles de minimisation des donnees."
)

# Simple PII redaction for prototype
_email_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_phone_re = re.compile(r"(\+?\d[\d \-()]{7,}\d)")


def redact_pii(text: str) -> str:
    if not text:
        return text
    redacted = _email_re.sub("[REDACTED_EMAIL]", text)
    redacted = _phone_re.sub("[REDACTED_PHONE]", redacted)
    return redacted


def mask_for_logs(text: str, keep=20) -> str:
    if not text:
        return text
    if len(text) <= keep * 2:
        return text
    return text[:keep] + "..." + text[-keep:]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: Request):
    payload = await req.json()
    message = payload.get("message") or payload.get("text") or ""
    user_id = payload.get("user_id", "anonymous")

    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    redacted_message = redact_pii(message) if REDACT_PII else message

    logger.info(f"[CHAT] user={user_id} message={mask_for_logs(message)} redacted={mask_for_logs(redacted_message)}")

    if not client:
        return {"reply": "ANTHROPIC_API_KEY non configuree. Definissez ANTHROPIC_API_KEY dans l'environnement."}

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": redacted_message},
            ],
        )
        reply = next(
            (block.text for block in response.content if block.type == "text"),
            "",
        )
    except anthropic.APIError as e:
        logger.exception("Claude API call failed")
        raise HTTPException(status_code=500, detail=f"Claude error: {e.message}")

    logger.info(f"[CHAT_REPLY] user={user_id} reply={mask_for_logs(reply)}")

    return {"reply": reply}


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    """WebSocket endpoint with streaming responses from Claude."""
    await ws.accept()
    if not client:
        await ws.send_text(json.dumps({"type": "error", "text": "ANTHROPIC_API_KEY non configuree."}))
        await ws.close()
        return

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            message = payload.get("message", data)

            redacted_message = redact_pii(message) if REDACT_PII else message

            # Stream the response token by token
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": redacted_message}],
            ) as stream:
                for text in stream.text_stream:
                    await ws.send_text(json.dumps({"type": "delta", "text": text}))

            await ws.send_text(json.dumps({"type": "done"}))
    except Exception:
        await ws.close()
