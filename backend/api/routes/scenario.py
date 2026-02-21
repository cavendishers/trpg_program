"""Scenario REST endpoints."""

from fastapi import APIRouter, HTTPException

from backend.dependencies import get_scenario_loader

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("")
async def list_scenarios():
    loader = get_scenario_loader()
    return loader.list_scenarios()


@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str):
    loader = get_scenario_loader()
    try:
        scenario = loader.load(scenario_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Scenario not found: {scenario_id}")
    # Return meta only (no keeper_guide for players)
    return {
        "meta": scenario.meta.model_dump(),
        "npcs": {
            k: {"name": v.name, "role": v.role, "description": v.description}
            for k, v in scenario.npcs.items()
        },
        "locations": {
            k: {"name": v.name, "atmosphere": v.atmosphere}
            for k, v in scenario.locations.items()
        },
    }
