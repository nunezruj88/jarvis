import os
import re

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
ENTITIES = {
    "clima": os.getenv("HA_WEATHER", ""),
    "luz": os.getenv("HA_LIGHT", ""),
    "solar": os.getenv("HA_SOLAR", ""),
    "calefaccion": os.getenv("HA_HEATING", ""),
}


@app.get("/entity/{entity_id}")
async def entity(entity_id: str):
    if not re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", entity_id) or entity_id not in ENTITIES.values():
        raise HTTPException(404, "Entidad fuera de la lista permitida.")
    url = os.getenv("HA_URL", "").rstrip("/")
    token = os.getenv("HA_TOKEN", "")
    if not url or not token:
        raise HTTPException(503, "Home Assistant está sin configurar.")
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False, trust_env=False) as client:
            response = await client.get(
                f"{url}/api/states/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()
            state = data["state"]
            attributes = data.get("attributes", {})
            if not isinstance(state, str) or state in {"unknown", "unavailable", ""}:
                raise ValueError("Estado no disponible")
            return {
                "entity_id": entity_id,
                "nombre": attributes.get("friendly_name", entity_id),
                "estado": state,
                "unidad": attributes.get("unit_of_measurement", ""),
            }
    except (httpx.HTTPError, KeyError, TypeError, ValueError, AttributeError):
        raise HTTPException(502, "Home Assistant no devolvió un estado disponible.") from None


@app.get("/state/{category}")
async def state(category: str):
    if not ENTITIES.get(category):
        raise HTTPException(404, "Consulta domótica sin configurar.")
    return await entity(ENTITIES[category])
