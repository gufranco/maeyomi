"""Which numbers each kind of card carries, so a request never asks for the rest.

A fighter carries health, attack and defence. A weapon carries attack, armour
carries defence, and a helper item carries one thing chosen by its sub-type
digit: health, herbs, magic points, or nothing for the two information items.
Asking an item for a number it does not carry makes every candidate disagree
with the request, so every surface builds its request from this one table.
"""

from enum import StrEnum
from typing import Final

from maeyomi.decoder.front_read import (
    SUPPORT_HIGHEST_HP_SUB_TYPE,
    SUPPORT_INFORMATION_SUB_TYPES,
    SUPPORT_POWER_POINT_SUB_TYPE,
)
from maeyomi.models.race import Race


class Carried(StrEnum):
    """One number a card can carry, named as the request field that holds it."""

    HP = "hp"
    ST = "st"
    DF = "df"
    PP = "pp"
    MP = "mp"


HEALTH_SUB_TYPE: Final = 0
MAGIC_SUB_TYPE: Final = SUPPORT_POWER_POINT_SUB_TYPE + 1
SUB_TYPE_FOR: Final[dict[Carried, int]] = {
    Carried.HP: HEALTH_SUB_TYPE,
    Carried.PP: SUPPORT_POWER_POINT_SUB_TYPE,
    Carried.MP: MAGIC_SUB_TYPE,
}


def carried(race: Race, job: int | None = None) -> tuple[Carried, ...]:
    """The numbers a card of this kind carries, in the order a card prints them."""
    if race.is_fighter:
        return (Carried.HP, Carried.ST, Carried.DF)
    if race.is_weapon:
        return (Carried.ST,)
    if race.is_armour:
        return (Carried.DF,)
    return _helper_item(HEALTH_SUB_TYPE if job is None else job)


def _helper_item(sub_type: int) -> tuple[Carried, ...]:
    """The one number a helper item carries, or none for an information item."""
    if sub_type <= SUPPORT_HIGHEST_HP_SUB_TYPE:
        return (Carried.HP,)
    if sub_type in SUPPORT_INFORMATION_SUB_TYPES:
        return ()
    if sub_type == SUPPORT_POWER_POINT_SUB_TYPE:
        return (Carried.PP,)
    return (Carried.MP,)
