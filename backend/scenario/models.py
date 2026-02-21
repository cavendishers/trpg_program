"""Scenario data models."""

from typing import Optional

from pydantic import BaseModel


class ScenarioMeta(BaseModel):
    id: str
    title: str
    era: str = "modern"
    player_count: dict = {"min": 1, "max": 4}
    difficulty: str = "introductory"
    synopsis: str = ""


class PlotPoint(BaseModel):
    id: str
    description: str
    depends_on: list[str] = []
    required_clues: list[str] = []
    key_discoveries: list[str] = []
    available_sources: list[str] = []
    hazards: list[str] = []


class Ending(BaseModel):
    id: str
    condition: str
    san_reward: str = "0"


class NPCTemplate(BaseModel):
    name: str
    role: str = ""
    description: str = ""
    personality: str = ""
    knows: list[str] = []
    dialogue_style: str = ""
    combat_stats: dict = {}
    abilities: list[dict] = []
    san_loss: dict = {}


class LocationArea(BaseModel):
    id: str
    description: str = ""
    searchable: bool = False
    possible_finds: list[str] = []
    hazards: list[str] = []
    requires_discovery: bool = False
    contains: list[str] = []


class Location(BaseModel):
    name: str
    atmosphere: str = ""
    areas: list[LocationArea] = []


class Clue(BaseModel):
    description: str
    importance: str = "normal"
    discovery: str = ""


class Scenario(BaseModel):
    meta: ScenarioMeta
    keeper_guide: str = ""
    key_plot_points: list[PlotPoint] = []
    endings: list[Ending] = []
    npcs: dict[str, NPCTemplate] = {}
    locations: dict[str, Location] = {}
    clues: dict[str, Clue] = {}
