"""The strongest first Barcode Battler cards, for the cheat code.

On the first device no field depends on another, so the strongest fighter is
every field at its ceiling: 19900 health, 9900 attack and 9900 defence, with
flag 05, which doubles its own attack. It is job 9 because the published
equipment table, in the note.com analysis by sakigomyway, lets job 9 equip
every weapon and multiplies the attack of weapon types 0 to 4 by one and a half.

The items are the matching weapon, armour and potion, each at its ceiling and
each of type 0, which job 9 can equip. Each carries a different flag: the
opponent's defence set to 0, one's own defence up by half, and better
accuracy. Every card goes through the solver and is decoded before it is
returned.
"""

from dataclasses import replace
from typing import Final

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.solve import MAX_HP, MAX_STAT, solve_first
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race

WEAPON_MASTER_JOB: Final = 9
FASTEST_DX: Final = 9
DOUBLE_OWN_ST: Final = 5
OPPONENT_DF_TO_ZERO: Final = 13
OWN_DF_UP_BY_HALF: Final = 6
OWN_ACCURACY_UP: Final = 3
ANY_FIGHTER_TYPE: Final = 0

type FirstCard = GeneratedCard[FirstBattlerCard]


def strongest_first_card(name: str = DEFAULT_CHEAT_NAME) -> FirstCard:
    """Every field of a front-read fighter at its ceiling."""
    return build_first_card(
        CardRequest(
            name=name,
            hp=Constraint.exactly(MAX_HP),
            st=Constraint.exactly(MAX_STAT),
            df=Constraint.exactly(MAX_STAT),
            race=Race.MECHANICAL,
            job=WEAPON_MASTER_JOB,
            speed=FASTEST_DX,
            special=DOUBLE_OWN_ST,
        )
    )


def strongest_first_items() -> tuple[FirstCard, ...]:
    """A lasting weapon, armour and potion at their ceilings, all equippable by the fighter."""
    return (
        _item("Cheat Blade", Race.WEAPON, OPPONENT_DF_TO_ZERO, ("st", MAX_STAT)),
        _item("Cheat Shield", Race.ARMOUR, OWN_DF_UP_BY_HALF, ("df", MAX_STAT)),
        _item("Cheat Potion", Race.SUPPORT_ITEM, OWN_ACCURACY_UP, ("hp", MAX_HP)),
    )


def _item(name: str, race: Race, flag: int, carries: tuple[str, int]) -> FirstCard:
    """One item of type 0 carrying one number."""
    field, amount = carries
    base = CardRequest(name=name, race=race, job=ANY_FIGHTER_TYPE, special=flag)
    return build_first_card(replace(base, **{field: Constraint.exactly(amount)}))


def build_first_card(request: CardRequest) -> FirstCard:
    """Solve one card, which the tests assert is always possible."""
    outcome = solve_first(request)
    if outcome.card is None:
        message = f"{request.name} cannot be built: {'; '.join(outcome.blockers)}"
        raise RuntimeError(message)
    return GeneratedCard(name=request.name, barcode=outcome.card.barcode, character=outcome.card)
