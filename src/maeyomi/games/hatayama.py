"""The battlers Hatayama Hatch no Pro Yakyuu News! Jitsumei Ban reads.

Epoch's Super Famicom baseball game of 1993 reads a code as a battler on the
Barcode Battler input of its Battle Baseball Board ($CF:F9CE). A code laid out
the way Epoch's own cards are is read in place ($CF:FA32): stamina from the
first three digits, attack and defense from the next two pairs, the type from
the eighth, the class from the ninth, and a wizard's magic from the eleventh
and twelfth; stamina above 199 needs a 9 as its third digit and a 5 as its
tenth, and then a type of 0, 1 or 2 adds 100 to attack, defense or both. Any
other code is read from the end ($CF:FAE6). A type of 5 or more is refused.
The last digit also picks the strategy ($CF:F7C4) and the graphic ($CF:F3B4)
on those two screens. Numbers show in hundreds. Confirmed against the game in
MAME.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat, required
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

WARRIOR: Final = 0
WIZARD: Final = 1
FIRST_WIZARD_CLASS: Final = 7
REFUSED_TYPE: Final = 5
BOOST: Final = 100
BIG_STAMINA: Final = 200
TOP_STAMINA: Final = 999
TOP_STAT: Final = 199
TOP_MP: Final = 99
HUNDRED: Final = 100
BLIZZARD: Final = 0
STRATEGIES: Final = 6
GRAPHIC_CODES: Final = ("0381108136502", "0401207336501", "0331010383501", "0320813183500")
"""$CF:F403: the four codes that pick a graphic by their place rather than their last digit."""
MP_KEY: Final = "mp"
BOOSTED_FIRST: Final = 2
MARKER_THIRD: Final = 9
MARKER_TENTH: Final = 5
BOOSTS: Final = {(True, False): 0, (False, True): 1, (True, True): 2}
PLAIN_TYPES: Final = (3, 4)


@dataclass(frozen=True, slots=True)
class HatayamaOrder:
    """A warrior or a wizard, what stamina, attack and defense must be, and its magic and type."""

    ident: int
    stats: tuple[Constraint, Constraint, Constraint]
    picks: tuple[tuple[str, int], ...] = ()


def decode_hatayama(code: str) -> DatachCard:
    """The battler a barcode is, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    digits = [int(character) for character in normalised.rjust(13, "0")]
    kind, cls, numbers = _in_place(digits) if _epoch_layout(digits) else _from_end(digits)
    traits = (kind, _strategy(digits), _graphic(normalised.rjust(13, "0"), digits))
    if kind >= REFUSED_TYPE:
        return DatachCard(normalised, Device.HATAYAMA, GameKind.NO_EFFECT, WARRIOR, (), traits)
    stamina, attack, defense, magic = numbers
    wizard = cls >= FIRST_WIZARD_CLASS
    stats = (
        GameStat("WHP", stamina * HUNDRED),
        GameStat("WST", attack * HUNDRED),
        GameStat("WDF", defense * HUNDRED),
        GameStat("WMP", magic if wizard else 0),
    )
    ident = WIZARD if wizard else WARRIOR
    return DatachCard(normalised, Device.HATAYAMA, GameKind.FIGHTER, ident, stats, traits)


def _epoch_layout(digits: list[int]) -> bool:
    """Whether the digits follow Epoch's own card layout, per $CF:F9CE."""
    if digits[0] < BOOSTED_FIRST:
        return digits[7] < REFUSED_TYPE or (digits[3] <= 1 and digits[5] <= 1)
    return digits[2] == MARKER_THIRD and digits[9] == MARKER_TENTH


def _in_place(digits: list[int]) -> tuple[int, int, tuple[int, int, int, int]]:
    """Type, class and numbers read where Epoch's cards print them."""
    boosted = digits[0] >= BOOSTED_FIRST and digits[2] == MARKER_THIRD and digits[9] == MARKER_TENTH
    kind = digits[7]
    attack_boost = boosted and kind in {0, 2}
    defense_boost = boosted and kind in {1, 2}
    numbers = (
        digits[0] * 100 + digits[1] * 10 + digits[2],
        BOOST * attack_boost + digits[3] * 10 + digits[4],
        BOOST * defense_boost + digits[5] * 10 + digits[6],
        digits[10] * 10 + digits[11],
    )
    return kind, digits[8], numbers


def _from_end(digits: list[int]) -> tuple[int, int, tuple[int, int, int, int]]:
    """Type, class and numbers worked from the last digits, per $CF:FAE6."""
    numbers = (
        (digits[11] >> 1) * 100 + digits[10] * 10 + digits[9],
        ((digits[10] + 5) % 10 + 2) * 10 + (digits[9] + 5) % 10,
        ((digits[9] + 7) % 10) * 10 + (digits[8] + 7) % 10,
        (digits[8] >> 2) * 10 + digits[10],
    )
    return digits[12], digits[5], numbers


def _strategy(digits: list[int]) -> int:
    """The strategy the last digit picks: its low three bits, and 6 or 7 its low two."""
    index = digits[12] & 7
    return index & 3 if index >= STRATEGIES else index


def _graphic(text: str, digits: list[int]) -> int:
    """The graphic a code picks: one of four special codes, or the last digit's low two bits."""
    return GRAPHIC_CODES.index(text) if text in GRAPHIC_CODES else digits[12] & 3


def build_hatayama(order: HatayamaOrder) -> DatachCard | None:
    """The first code Epoch's layout reads as the battler ordered, or None."""
    wanted = dict(order.picks)
    bodies = ("".join(map(str, digits)) for digits in _candidates(order, wanted))
    cards = (decode_hatayama(body + str(expected_check_digit(body))) for body in bodies)
    return next((card for card in cards if _meets(card, order, wanted)), None)


def _candidates(order: HatayamaOrder, wanted: dict[str, int]) -> Iterator[list[int]]:
    """Every twelve-digit body in Epoch's layout with the numbers and choices ordered."""
    stamina, attack, defense = (
        [value for value in range(top + 1) if constraint.admits(value * HUNDRED)]
        for constraint, top in zip(order.stats, (TOP_STAMINA, TOP_STAT, TOP_STAT), strict=True)
    )
    classes = [FIRST_WIZARD_CLASS] if order.ident == WIZARD else [0]
    magic = [wanted.get(MP_KEY, TOP_MP)] if order.ident == WIZARD else [0]
    for hp, st, df, cls, mp in itertools.product(stamina, attack, defense, classes, magic):
        body = _body(hp, st, df, cls, mp)
        if body is not None:
            yield body


def _body(hp: int, st: int, df: int, cls: int, mp: int) -> list[int] | None:
    """The layout that reads as these numbers, or None when no layout does."""
    needed = (st >= BOOST, df >= BOOST)
    if hp < BIG_STAMINA and needed == (False, False):
        kind = PLAIN_TYPES[0]
        return [*_split(hp, 3), *_split(st, 2), *_split(df, 2), kind, cls, 0, *_split(mp, 2)]
    if hp < BIG_STAMINA or hp % 10 != MARKER_THIRD:
        return None
    kind = BOOSTS.get(needed, PLAIN_TYPES[0])
    return [
        *_split(hp, 3),
        *_split(st % BOOST, 2),
        *_split(df % BOOST, 2),
        kind,
        cls,
        MARKER_TENTH,
        *_split(mp, 2),
    ]


def _split(value: int, width: int) -> list[int]:
    """A number as its decimal digits, zero-padded to a width."""
    return [int(character) for character in f"{value:0{width}d}"]


def _meets(card: DatachCard, order: HatayamaOrder, wanted: dict[str, int]) -> bool:
    """Whether a read card is the battler ordered, numbers and magic alike."""
    numbers = (card.value("WHP"), card.value("WST"), card.value("WDF"))
    admitted = all(
        constraint.admits(value) for constraint, value in zip(order.stats, numbers, strict=True)
    )
    magic = MP_KEY not in wanted or card.value("WMP") == wanted[MP_KEY]
    return card.kind is GameKind.FIGHTER and card.ident == order.ident and admitted and magic


def strongest_hatayama() -> DatachCard:
    """A wizard with stamina, attack, defense and magic at the most the game reads."""
    top = (
        Constraint.exactly(TOP_STAMINA * HUNDRED),
        Constraint.exactly(TOP_STAT * HUNDRED),
        Constraint.exactly(TOP_STAT * HUNDRED),
    )
    card = build_hatayama(HatayamaOrder(WIZARD, top, ((MP_KEY, TOP_MP),)))
    return required(card, "the strongest Hatayama Hatch battler cannot be printed")
