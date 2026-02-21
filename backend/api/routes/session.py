"""Game session management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.game_engine import GameEngine
from backend.dependencies import (
    get_ai_provider,
    get_character_service,
    get_scenario_loader,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# In-memory session store (MVP)
_sessions: dict[str, GameEngine] = {}


class CreateSessionRequest(BaseModel):
    scenario_id: str


@router.post("")
async def create_session(req: CreateSessionRequest):
    loader = get_scenario_loader()
    try:
        scenario = loader.load(req.scenario_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Scenario not found: {req.scenario_id}")

    provider = get_ai_provider()
    chars = get_character_service()
    engine = GameEngine(provider, scenario, chars)
    _sessions[engine.session.id] = engine
    return {"session_id": engine.session.id, "scenario": scenario.meta.title}


@router.get("/{session_id}")
async def get_session(session_id: str):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    return {
        "id": engine.session.id,
        "scenario_id": engine.session.scenario_id,
        "phase": engine.state.phase.value,
    }


@router.post("/{session_id}/start")
async def start_session(session_id: str):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    # Try loading auto-save first
    loaded = engine.load_from_file("auto")
    if not loaded:
        engine.start_game()
        engine.begin_exploration()
    return {"phase": engine.state.phase.value, "resumed": loaded}


@router.get("/{session_id}/state")
async def get_game_state(session_id: str):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    chars = engine.characters
    return {
        "phase": engine.state.phase.value,
        "party": [c.model_dump() for c in chars.list_party()],
        "npcs": [c.model_dump() for c in chars.list_active_npcs()],
        "plot_progress": engine.guardian.generate_progress_prompt(),
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]
    return {"status": "deleted"}


class SaveRequest(BaseModel):
    slot: str = "auto"


@router.post("/{session_id}/save")
async def save_session(session_id: str, req: SaveRequest = SaveRequest()):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    path = engine.save_to_file(req.slot)
    return {"status": "saved", "slot": req.slot, "path": str(path)}


@router.post("/{session_id}/load")
async def load_session(session_id: str, req: SaveRequest = SaveRequest()):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    ok = engine.load_from_file(req.slot)
    if not ok:
        raise HTTPException(404, f"Save not found for slot: {req.slot}")
    return {
        "status": "loaded",
        "slot": req.slot,
        "phase": engine.state.phase.value,
    }


@router.get("/{session_id}/saves")
async def list_saves(session_id: str):
    from backend.core.game_engine import GameEngine
    return {"saves": GameEngine.list_saves(session_id)}


def get_session_engine(session_id: str) -> GameEngine:
    """Helper for the WebSocket game route."""
    engine = _sessions.get(session_id)
    if not engine:
        raise KeyError(f"Session not found: {session_id}")
    return engine
