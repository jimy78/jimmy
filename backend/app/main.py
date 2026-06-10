from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import json
import uuid
import logging
import anthropic

from .database import init_db, seed_demo_data, SessionLocal, ChatHistory
from .tools import TOOLS, execute_tool

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
MAX_TOOL_ROUNDS = 10

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

SYSTEM_PROMPT = """\
Vous etes un assistant RH expert, complet et professionnel. Repondez de maniere concise et conforme au RGPD.
Si la requete contient des informations personnelles identifiables, appliquez les regles de minimisation des donnees.

Vous avez acces a un ensemble complet d'outils RH pour gerer toutes les situations :

CONSULTATION :
- lookup_employee : Rechercher un employe (par nom ou ID)
- get_leave_balance : Solde de conges et RTT
- get_leave_requests : Historique des demandes de conges
- get_absences : Liste des absences
- search_policy : Consulter les politiques internes (conges, teletravail, maladie, frais, contrat, ethique, RGPD, bien-etre, astreintes)
- list_department_employees : Liste des employes d'un departement
- get_org_chart : Organigramme (manager, equipe, N-1)
- get_payslip_info : Bulletin de paie (brut, net, primes, cotisations)
- get_contract_info : Informations contractuelles (type, periode d'essai, anciennete)
- get_training_catalog : Catalogue des formations
- get_training_budget : Budget formation et inscriptions
- get_expenses : Notes de frais
- search_job_openings : Postes ouverts (mobilite interne et externe)
- get_performance_review : Evaluations de performance
- get_onboarding_checklist : Checklist d'integration
- calculate_seniority : Calcul d'anciennete et droits associes
- team_analytics : Statistiques d'equipe (effectifs, absenteisme, turnover)
- search_directory : Annuaire interne

ACTIONS :
- request_leave : Poser une demande de conge
- log_absence : Declarer une absence (maladie, enfant malade, accident)
- enroll_training : S'inscrire a une formation
- submit_expense : Soumettre une note de frais

REGLES :
1. Utilisez TOUJOURS les outils pour repondre avec des donnees reelles — ne devinez jamais.
2. Pour les questions sur les droits ou procedures, consultez d'abord search_policy.
3. Pour les questions sur un employe, commencez par lookup_employee si l'ID n'est pas connu.
4. Repondez en francais. Soyez precis avec les chiffres et les dates.
5. Si une action modifie des donnees, confirmez ce qui a ete fait.
6. Ne divulguez pas les salaires a des tiers non autorises.
"""

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


# ---------------------------------------------------------------------------
# Conversation history helpers
# ---------------------------------------------------------------------------

def load_history(session_id: str) -> list[dict]:
    """Load conversation history from the database."""
    db = SessionLocal()
    try:
        rows = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.id)
            .all()
        )
        messages = []
        for row in rows:
            messages.append({"role": row.role, "content": row.content})
        return messages
    finally:
        db.close()


def save_message(session_id: str, role: str, content: str):
    """Persist a single message to the database."""
    db = SessionLocal()
    try:
        db.add(ChatHistory(session_id=session_id, role=role, content=content))
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Agentic loop: call Claude with tools, execute tools, loop until done
# ---------------------------------------------------------------------------

def run_agent(messages: list[dict]) -> str:
    """Run the agentic tool loop and return the final text reply."""
    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # If Claude is done, extract text
        if response.stop_reason == "end_turn":
            return next(
                (block.text for block in response.content if block.type == "text"),
                "",
            )

        # Claude wants to use tools
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_use_blocks:
            return next(
                (block.text for block in response.content if block.type == "text"),
                "",
            )

        # Append assistant response (with tool_use blocks)
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and collect results
        tool_results = []
        for tool_block in tool_use_blocks:
            logger.info(f"[TOOL] Calling {tool_block.name} with {tool_block.input}")
            result = execute_tool(tool_block.name, tool_block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    # Fallback if we exhausted rounds
    return "Desole, je n'ai pas pu completer la recherche. Veuillez reformuler votre question."


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()
    seed_demo_data()
    logger.info("Database initialized and demo data seeded.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: Request):
    payload = await req.json()
    message = payload.get("message") or payload.get("text") or ""
    user_id = payload.get("user_id", "anonymous")
    session_id = payload.get("session_id") or str(uuid.uuid4())

    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    redacted_message = redact_pii(message) if REDACT_PII else message

    logger.info(f"[CHAT] user={user_id} session={session_id} message={mask_for_logs(message)}")

    if not client:
        return {"reply": "ANTHROPIC_API_KEY non configuree.", "session_id": session_id}

    # Load history and append new message
    messages = load_history(session_id)
    messages.append({"role": "user", "content": redacted_message})
    save_message(session_id, "user", redacted_message)

    try:
        reply = run_agent(messages)
    except anthropic.APIError as e:
        logger.exception("Claude API call failed")
        raise HTTPException(status_code=500, detail=f"Claude error: {e.message}")

    # Save assistant reply
    save_message(session_id, "assistant", reply)

    logger.info(f"[CHAT_REPLY] user={user_id} reply={mask_for_logs(reply)}")

    return {"reply": reply, "session_id": session_id}


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    """WebSocket endpoint with streaming responses from Claude."""
    await ws.accept()
    if not client:
        await ws.send_text(json.dumps({"type": "error", "text": "ANTHROPIC_API_KEY non configuree."}))
        await ws.close()
        return

    session_id = str(uuid.uuid4())
    await ws.send_text(json.dumps({"type": "session", "session_id": session_id}))

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            message = payload.get("message", data)

            redacted_message = redact_pii(message) if REDACT_PII else message

            # Load history for multi-turn
            messages = load_history(session_id)
            messages.append({"role": "user", "content": redacted_message})
            save_message(session_id, "user", redacted_message)

            # For WebSocket we stream the final response but run tools synchronously
            # First, run tools loop until Claude is ready to give a text response
            for _ in range(MAX_TOOL_ROUNDS):
                response = client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages,
                )

                if response.stop_reason == "end_turn":
                    break

                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                if not tool_use_blocks:
                    break

                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for tool_block in tool_use_blocks:
                    logger.info(f"[WS_TOOL] Calling {tool_block.name}")
                    result = execute_tool(tool_block.name, tool_block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result,
                    })
                    # Notify the client that a tool is being used
                    await ws.send_text(json.dumps({
                        "type": "tool",
                        "name": tool_block.name,
                        "input": tool_block.input,
                    }))

                messages.append({"role": "user", "content": tool_results})

            # Now stream the final text response
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            ) as stream:
                full_reply = []
                for text in stream.text_stream:
                    full_reply.append(text)
                    await ws.send_text(json.dumps({"type": "delta", "text": text}))

            reply_text = "".join(full_reply)
            save_message(session_id, "assistant", reply_text)
            await ws.send_text(json.dumps({"type": "done"}))

    except Exception:
        await ws.close()
