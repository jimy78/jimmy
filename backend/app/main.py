from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import logging
import openai

# Basic logger
logger = logging.getLogger("hr-agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Read env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
REDACT_PII = os.getenv("REDACT_PII", "true").lower() in ("1","true","yes")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set. OpenAI calls will fail until it is configured.")
else:
    openai.api_key = OPENAI_API_KEY

app = FastAPI(title="HR Agent Prototype - OpenAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple PII redaction for prototype
_email_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_phone_re = re.compile(r"(\+?\d[\d \-()]{7,}\d)")

def redact_pii(text: str) -> str:
    if not text:
        return text
    # redact emails
    redacted = _email_re.sub("[REDACTED_EMAIL]", text)
    # redact phones
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

    # Redact PII if enabled
    redacted_message = redact_pii(message) if REDACT_PII else message

    logger.info(f"[CHAT] user={{user_id}} message={{mask_for_logs(message)}} redacted={{mask_for_logs(redacted_message)}}")

    if not OPENAI_API_KEY:
        return {"reply": "OpenAI API key not configured. Set OPENAI_API_KEY in environment."}

    system_prompt = (
        "Vous êtes un assistant RH expert. Répondez de manière concise, professionnelle et conforme au RGPD. "
        "Si la requête contient des informations personnelles identifiables, appliquez les règles de minimisation des données."
    )

    try:
        # Using Chat Completions API (sync) for prototype
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": redacted_message},
            ],
            max_tokens=800,
            temperature=0.2,
        )
        reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.exception("OpenAI call failed")
        raise HTTPException(status_code=500, detail=f"OpenAI error: {{str(e)}}")

    logger.info(f"[CHAT_REPLY] user={{user_id}} reply={{mask_for_logs(reply)}}")

    return {"reply": reply}

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            # Basic echo for websocket; production would stream model response
            await ws.send_text(f"Echo: {{data}}")
    except Exception:
        await ws.close()