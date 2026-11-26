import asyncio
import os
import re
import sqlite3
import unicodedata
from contextlib import asynccontextmanager, closing
from pathlib import Path
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

DB = os.getenv("HISTORY_DB", "history.sqlite3")
MODEL = os.getenv("JARVIS_MODEL", "local")
RECENT = 20
SYSTEM = (
    "Eres Jarvis, un asistente en español. Responde de forma breve. "
    "No controlas dispositivos ni puedes conocer estados actuales de la casa. "
    "Para consultas domóticas indica que se usen los botones del portal. "
    "No presentes estados mencionados en el historial como datos actuales."
)
TOPICS = {
    "clima": ("Clima", r"clima|que tiempo|tiempo (?:actual|hace)|meteorolog\w*|llueve|lluvia"),
    "luz": ("Luz Shelly", r"luz|luces|shelly|dispositivos"),
    "solar": ("Energía solar", r"solar|fotovoltaic\w*|placas"),
    "calefaccion": ("Calefacción", r"calefaccion|circuito|radiadores"),
}
STATES = {
    "on": "encendido", "off": "apagado", "partlycloudy": "parcialmente nublado",
    "sunny": "soleado", "clear-night": "despejado", "cloudy": "nublado",
    "rainy": "lluvia", "pouring": "lluvia intensa", "fog": "niebla",
}


@asynccontextmanager
async def lifespan(app):
    with closing(sqlite3.connect(DB)) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY, conversation TEXT NOT NULL,
                role TEXT NOT NULL, content TEXT NOT NULL,
                model_context INTEGER NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS conversation_order ON messages(conversation, id)")
    async with httpx.AsyncClient(trust_env=False) as client:
        app.state.http = client
        yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


class Chat(BaseModel):
    text: str = Field(min_length=1, max_length=6000)

    @field_validator("text")
    @classmethod
    def trim(cls, text):
        if not text.strip():
            raise ValueError("Escribe un mensaje.")
        return text.strip()


def conversation(x_jarvis_conversation: UUID = Header()) -> str:
    return str(x_jarvis_conversation)


def recent(session, *, for_model=False):
    with closing(sqlite3.connect(DB)) as connection:
        rows = connection.execute(
            """SELECT role, content FROM messages WHERE conversation = ?
               AND (? = 0 OR model_context = 1) ORDER BY id DESC LIMIT ?""",
            (session, for_model, RECENT),
        ).fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def save_exchange(session, text, reply, *, model_context):
    with closing(sqlite3.connect(DB)) as connection, connection:
        connection.executemany(
            """INSERT INTO messages(conversation, role, content, model_context)
               VALUES (?, ?, ?, ?)""",
            [(session, "user", text, model_context), (session, "assistant", reply, model_context)],
        )
        connection.execute(
            """DELETE FROM messages WHERE conversation = ? AND id NOT IN (
                SELECT id FROM messages WHERE conversation = ? ORDER BY id DESC LIMIT ?
            )""",
            (session, session, RECENT),
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/history")
def history(session: str = Depends(conversation)):
    return {"messages": recent(session)}


@app.delete("/api/history")
def clear_history(session: str = Depends(conversation)):
    with closing(sqlite3.connect(DB)) as connection, connection:
        connection.execute("DELETE FROM messages WHERE conversation = ?", (session,))
    return {"messages": []}


async def read_home(category):
    label, _ = TOPICS[category]
    try:
        response = await app.state.http.get(f"http://ha-bridge:8090/state/{category}", timeout=10)
        if response.status_code == 404:
            return f"{label}: consulta sin configurar."
        response.raise_for_status()
        item = response.json()
        raw = item["estado"]
        state = STATES.get(raw, raw)
        if category == "luz":
            state = {"on": "encendida", "off": "apagada"}.get(raw, state)
        return f"{label}: {state} {item['unidad'] or ''}".rstrip() + "."
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return f"{label}: no pude obtener un estado actual de Home Assistant."


@app.post("/api/chat")
async def chat(body: Chat, session: str = Depends(conversation)):
    query = unicodedata.normalize("NFKD", body.text.casefold()).encode("ascii", "ignore").decode()
    categories = [key for key, (_, pattern) in TOPICS.items() if re.search(rf"\b(?:{pattern})\b", query)]
    if categories:
        if re.search(r"\b(?:enciende|apaga|activa|desactiva|sube|baja|ajusta|cambia|encender|apagar)\b", query):
            reply = "Puedo consultar el estado de tu casa. El control de dispositivos está deshabilitado."
        else:
            reply = "\n".join(await asyncio.gather(*(read_home(category) for category in categories)))
    else:
        try:
            response = await app.state.http.post(
                "http://litellm:4000/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('LITELLM_KEY', '')}"},
                json={"model": MODEL, "messages": [
                    {"role": "system", "content": SYSTEM},
                    *recent(session, for_model=True),
                    {"role": "user", "content": body.text},
                ]},
                timeout=180,
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"].strip()
            if not reply:
                raise ValueError("Respuesta vacía")
        except (httpx.HTTPError, KeyError, IndexError, AttributeError, TypeError, ValueError):
            raise HTTPException(502, "La IA no respondió. Revisa LiteLLM y el modelo configurado.") from None
    save_exchange(session, body.text, reply, model_context=not categories)
    return {"reply": reply}


app.mount("/", StaticFiles(directory=Path(__file__).with_name("static"), html=True), name="portal")
