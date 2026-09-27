"""The strongest item of every kind, handed out beside the cheat card.

Each item carries the most its digits can hold: a two-digit slice read in
hundreds for a weapon or armour, three digits for health, and a plain count up
to 99 for herbs and magic points. Every one goes through the solver, so each is
decoded and compared like any other card before it is returned.

Each item also passes a special power to whoever uses it, per the note.com
analysis by sakigomyway. No two share one, and each is the largest documented
effect of its family: the cheat fighter already doubles its own attack, so the
items take the opponent's defence, health, strength, and special powers, and
add to their holder's defence. Whether several items' powers stack is not
documented anywhere, so nothing here depends on it.
"""

from dataclasses import replace
from typing import Final

from maeyomi.generator.carried import SUB_TYPE_FOR, Carried
from maeyomi.generator.front_solver import MAX_DIGIT_PAIR, MAX_HP_DISPLAY
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import MAX_POINTS, CardRequest
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.constraint import Constraint
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race

MAX_ITEM_STAT: Final = MAX_DIGIT_PAIR * DISPLAY_SCALE
OPPONENT_DEFENCE_CUT_BY_EIGHTY: Final = 27
OWN_DEFENCE_UP_BY_HALF: Final = 22
OPPONENT_HEALTH_HALVED: Final = 29
OPPONENT_ATTACK_HALVED: Final = 24
OPPONENT_POWERS_CANCELLED: Final = 45
ITEM_ABILITIES: Final[dict[str, int]] = {
    "Cheat Blade": OPPONENT_DEFENCE_CUT_BY_EIGHTY,
    "Cheat Shield": OWN_DEFENCE_UP_BY_HALF,
    "Cheat Potion": OPPONENT_HEALTH_HALVED,
    "Cheat Herbs": OPPONENT_ATTACK_HALVED,
    "Cheat Crystal": OPPONENT_POWERS_CANCELLED,
}


def strongest_items() -> tuple[GeneratedCard, ...]:
    """A lasting weapon, armour, and one helper item of each kind, all at the maximum."""
    return tuple(build_item(request) for request in _requests())


def _requests() -> tuple[CardRequest, ...]:
    """One request per item, each asking for the ceiling of what it carries."""
    names = iter(ITEM_ABILITIES)
    return (
        _item(next(names), Race.WEAPON, 0, st=Constraint.exactly(MAX_ITEM_STAT)),
        _item(next(names), Race.ARMOUR, 0, df=Constraint.exactly(MAX_ITEM_STAT)),
        _helper(next(names), Carried.HP, Constraint.exactly(MAX_HP_DISPLAY)),
        _helper(next(names), Carried.PP, Constraint.exactly(MAX_POINTS)),
        _helper(next(names), Carried.MP, Constraint.exactly(MAX_POINTS)),
    )


def _helper(name: str, gives: Carried, amount: Constraint) -> CardRequest:
    """A helper item that gives one thing."""
    return _item(name, Race.SUPPORT_ITEM, SUB_TYPE_FOR[gives], **{gives.value: amount})


def _item(name: str, race: Race, job: int, **carried: Constraint) -> CardRequest:
    """One item request with its name's special power."""
    base = CardRequest(name=name, race=race, job=job, special=ITEM_ABILITIES[name])
    return replace(base, **carried)


def build_item(request: CardRequest) -> GeneratedCard:
    """Solve one item, which every test asserts is always possible."""
    outcome = solve(request)
    if outcome.barcode is None or outcome.character is None:
        message = f"{request.name} cannot be built: {'; '.join(outcome.blockers)}"
        raise RuntimeError(message)
    return GeneratedCard(name=request.name, barcode=outcome.barcode, character=outcome.character)
