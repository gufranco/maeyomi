"""Which Barcode Battler II fighters can use which items.

Source: the equipment table in the note.com analysis of the Barcode Battler II
by sakigomyway, whose author entered printed codes on a device. An item's type
is its job digit. Weapons and armour share one table and no magician can hold
either. Information items and herbs fit everyone. Health and magic items follow
their own tables, and a magic item fits no warrior.
"""

from typing import Final

from maeyomi.generator.carried import Carried, carried
from maeyomi.models.character import HIGHEST_WARRIOR_JOB, BarcodeBattlerCharacter

ALL_JOBS: Final = tuple(range(10))

_GEAR: Final[dict[int, frozenset[int]]] = {
    0: frozenset({0, 7, 9}),
    1: frozenset({0, 1, 7}),
    2: frozenset({0, 2, 7}),
    3: frozenset({0, 3, 7, 8}),
    4: frozenset({0, 4, 8}),
    5: frozenset({0, 5, 8}),
    6: frozenset({0, 6, 8}),
}
_HEALTH: Final[dict[int, frozenset[int]]] = {
    0: frozenset({0, 1}),
    1: frozenset({0, 2}),
    2: frozenset({0, 3}),
    3: frozenset({0, 4}),
    9: frozenset({0, 1, 2, 3, 4}),
}
_HEALTH_DEFAULT: Final = frozenset({0})
_MAGIC: Final[dict[int, frozenset[int]]] = {
    7: frozenset({7, 8}),
    8: frozenset({7, 9}),
    9: frozenset({7, 8, 9}),
}


def can_equip(job: int, item: BarcodeBattlerCharacter) -> bool:
    """Whether a fighter of this job can use this item."""
    if item.race.is_fighter:
        return False
    if item.race.is_weapon or item.race.is_armour:
        return item.job in _GEAR.get(job, frozenset())
    gives = carried(item.race, item.job)
    if Carried.HP in gives:
        return item.job in _HEALTH.get(job, _HEALTH_DEFAULT)
    if Carried.MP in gives:
        return job > HIGHEST_WARRIOR_JOB and item.job in _MAGIC[job]
    return True


def equipping_jobs(item: BarcodeBattlerCharacter) -> tuple[int, ...]:
    """Every job that can use this item, ascending."""
    return tuple(job for job in ALL_JOBS if can_equip(job, item))
