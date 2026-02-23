"""Game session management endpoints."""

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.game_engine import GameEngine, SAVES_DIR
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
    force_new: bool = False


@router.post("")
async def create_session(req: CreateSessionRequest):
    loader = get_scenario_loader()
    try:
        scenario = loader.load(req.scenario_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Scenario not found: {req.scenario_id}")

    # Auto-resume: check for existing save unless force_new
    if not req.force_new:
        existing = GameEngine.find_latest_save(req.scenario_id)
        if existing:
            provider = get_ai_provider()
            chars = get_character_service()
            engine = GameEngine(provider, scenario, chars)
            engine.load_save_data(existing["data"])
            old_id = existing["data"].get("session", {}).get("id", engine.session.id)
            engine.session.id = old_id
            _sessions[old_id] = engine
            return {
                "session_id": old_id,
                "scenario": scenario.meta.title,
                "resumed": True,
            }

    provider = get_ai_provider()
    chars = get_character_service()
    engine = GameEngine(provider, scenario, chars)
    _sessions[engine.session.id] = engine
    return {"session_id": engine.session.id, "scenario": scenario.meta.title, "resumed": False}


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


class ResumeRequest(BaseModel):
    filename: str


class SessionCharacterRequest(BaseModel):
    name: str
    player_name: str = "Player 1"
    occupation: str = ""
    age: int = 25


class GeneratePartyRequest(BaseModel):
    count: int = 3


@router.get("/{session_id}/characters")
async def list_session_characters(session_id: str):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    party = engine.characters.list_party()
    return [c.model_dump() for c in party]


@router.post("/{session_id}/characters")
async def add_session_character(session_id: str, req: SessionCharacterRequest):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    char = engine.characters.create_pc(
        name=req.name,
        player_name=req.player_name,
        occupation=req.occupation,
        age=req.age,
    )
    return char.model_dump()


@router.delete("/{session_id}/characters/{char_id}")
async def remove_session_character(session_id: str, char_id: str):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    if char_id not in engine.characters._characters:
        raise HTTPException(404, "Character not found")
    del engine.characters._characters[char_id]
    return {"status": "deleted"}


@router.post("/{session_id}/characters/generate")
async def generate_party(session_id: str, req: GeneratePartyRequest):
    engine = _sessions.get(session_id)
    if not engine:
        raise HTTPException(404, "Session not found")
    characters = await engine.generate_party(req.count)
    return [c.model_dump() for c in characters]


@router.post("/resume")
async def resume_session(req: ResumeRequest):
    """Create a new session from a save file."""
    path = SAVES_DIR / req.filename
    if not path.exists():
        raise HTTPException(404, "Save file not found")
    try:
        save_data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        raise HTTPException(422, "Save file is corrupted")

    scenario_id = save_data.get("scenario_id", "")
    loader = get_scenario_loader()
    try:
        scenario = loader.load(scenario_id)
    except FileNotFoundError:
        raise HTTPException(409, f"Scenario not found: {scenario_id}")

    provider = get_ai_provider()
    chars = get_character_service()
    engine = GameEngine(provider, scenario, chars)
    engine.load_save_data(save_data)

    # Reuse original session ID so auto-save overwrites the same file
    old_id = save_data.get("session", {}).get("id", engine.session.id)
    engine.session.id = old_id
    _sessions[old_id] = engine

    return {
        "session_id": old_id,
        "scenario": scenario.meta.title,
        "phase": engine.state.phase.value,
        "resumed": True,
    }


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
