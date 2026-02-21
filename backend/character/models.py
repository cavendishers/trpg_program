"""CoC 7e character data models."""

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.rules.character_calc import Characteristics, DerivedStats


COC_DEFAULT_SKILLS: dict[str, int] = {
    "会计": 5, "人类学": 1, "估价": 5, "考古学": 1, "魅惑": 15,
    "攀爬": 20, "计算机使用": 5, "信用评级": 0, "克苏鲁神话": 0,
    "乔装": 5, "闪避": 0, "驾驶": 20, "电气维修": 10, "电子学": 1,
    "话术": 5, "格斗(斗殴)": 25, "射击(手枪)": 20, "射击(步枪)": 25,
    "急救": 30, "历史": 5, "恐吓": 15, "跳跃": 20, "外语": 1,
    "法律": 5, "图书馆使用": 20, "聆听": 20, "锁匠": 1, "机械维修": 10,
    "医学": 1, "博物学": 10, "导航": 10, "神秘学": 5, "操作重型机械": 1,
    "说服": 10, "摄影": 5, "精神分析": 1, "心理学": 10, "骑术": 5,
    "科学": 1, "妙手": 10, "侦查": 25, "潜行": 20, "生存": 10,
    "游泳": 20, "投掷": 20, "追踪": 10,
}


class Skill(BaseModel):
    name: str
    base_value: int
    current_value: int
    used_successfully: bool = False


class Backstory(BaseModel):
    ideology: str = ""
    significant_people: str = ""
    meaningful_locations: str = ""
    treasured_possessions: str = ""
    traits: str = ""


class CoCCharacter(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    name: str
    is_npc: bool = False
    player_name: Optional[str] = None
    occupation: str = ""
    age: int = 25

    characteristics: Characteristics
    derived: DerivedStats

    skills: dict[str, Skill] = {}
    backstory: Backstory = Field(default_factory=Backstory)
    inventory: list[str] = []
    conditions: list[str] = []

    # NPC-specific
    disposition: Optional[int] = None
    known_info: Optional[list[str]] = None
    dialogue_style: Optional[str] = None
