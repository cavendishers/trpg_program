"""Character CRUD endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.dependencies import get_character_service

router = APIRouter(prefix="/api/characters", tags=["characters"])


class CreateCharacterRequest(BaseModel):
    name: str
    player_name: str
    occupation: str = ""
    age: int = 25


class UpdateSkillRequest(BaseModel):
    skill_name: str
    value: int


@router.post("")
async def create_character(req: CreateCharacterRequest):
    svc = get_character_service()
    char = svc.create_pc(
        name=req.name,
        player_name=req.player_name,
        occupation=req.occupation,
        age=req.age,
    )
    return char.model_dump()


@router.get("/{character_id}")
async def get_character(character_id: str):
    svc = get_character_service()
    char = svc.get_character(character_id)
    if not char:
        raise HTTPException(404, "Character not found")
    return char.model_dump()


@router.get("")
async def list_characters():
    svc = get_character_service()
    party = svc.list_party()
    npcs = svc.list_active_npcs()
    return {
        "party": [c.model_dump() for c in party],
        "npcs": [c.model_dump() for c in npcs],
    }
