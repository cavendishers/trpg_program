"""CoC 7e character attribute calculations."""

from pydantic import BaseModel, Field


class Characteristics(BaseModel):
    STR: int = Field(ge=1, le=99)
    CON: int = Field(ge=1, le=99)
    SIZ: int = Field(ge=1, le=99)
    DEX: int = Field(ge=1, le=99)
    APP: int = Field(ge=1, le=99)
    INT: int = Field(ge=1, le=99)
    POW: int = Field(ge=1, le=99)
    EDU: int = Field(ge=1, le=99)


class DerivedStats(BaseModel):
    hp_max: int
    hp: int
    san_max: int
    san: int
    mp_max: int
    mp: int
    luck: int
    damage_bonus: str
    build: int
    move_rate: int


_DB_TABLE = [
    (64, "-2", -2),
    (84, "-1", -1),
    (124, "0", 0),
    (164, "+1d4", 1),
    (204, "+1d6", 2),
    (284, "+2d6", 3),
    (364, "+3d6", 4),
    (444, "+4d6", 5),
    (524, "+5d6", 6),
]


def _damage_bonus_and_build(str_siz: int) -> tuple[str, int]:
    for threshold, db, build in _DB_TABLE:
        if str_siz <= threshold:
            return db, build
    return "+5d6", 6


def _base_move_rate(strength: int, dex: int, siz: int) -> int:
    if strength < siz and dex < siz:
        return 7
    if strength >= siz and dex >= siz:
        return 9
    return 8


def calculate_derived_stats(chars: Characteristics, luck: int) -> DerivedStats:
    hp_max = (chars.CON + chars.SIZ) // 10
    db, build = _damage_bonus_and_build(chars.STR + chars.SIZ)
    move = _base_move_rate(chars.STR, chars.DEX, chars.SIZ)
    mp_max = chars.POW // 5
    return DerivedStats(
        hp_max=hp_max,
        hp=hp_max,
        san_max=chars.POW,
        san=chars.POW,
        mp_max=mp_max,
        mp=mp_max,
        luck=luck,
        damage_bonus=db,
        build=build,
        move_rate=move,
    )


def roll_characteristics(rng=None) -> Characteristics:
    """Roll random characteristics using CoC 7e rules (3d6*5 or 2d6+6*5)."""
    import random
    r = rng or random.Random()

    def roll_3d6x5():
        return sum(r.randint(1, 6) for _ in range(3)) * 5

    def roll_2d6p6x5():
        return (sum(r.randint(1, 6) for _ in range(2)) + 6) * 5

    return Characteristics(
        STR=roll_3d6x5(),
        CON=roll_3d6x5(),
        SIZ=roll_2d6p6x5(),
        DEX=roll_3d6x5(),
        APP=roll_3d6x5(),
        INT=roll_2d6p6x5(),
        POW=roll_3d6x5(),
        EDU=roll_2d6p6x5(),
    )
