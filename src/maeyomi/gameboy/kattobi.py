"""Kattobi Road, Namco 1993: a Barcode Boy racing game that reads a card as a car.

The rule is the game's own, followed through its code after a scan and checked
against every code it read in MAME. Only the last five digits count, e0 to e4.
With x = 10*e0 + e1 and y = 10*e3 + e4, the car is model ((x+1)*y - 1) mod 256
of the 256 the game keeps. Power is the model's less 30, plus
((e2+1) * (10*e0 + e3 + 1)) mod 60; torque is its less 50, plus
((e2+1) * (10*e1 + e4 + 1)) mod 100; a model under 30 or 50 is held there.
Weight is the model's.
"""

from dataclasses import dataclass
from functools import cache
from itertools import product
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat, required
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.gameboy.kattobi_tables import CATEGORIES, ENGLISH, MODELS, NAMES
from maeyomi.models.device import Device

POWER_KEY: Final = "KPW"
WEIGHT_KEY: Final = "KWT"
STAT_KEYS: Final[tuple[str, ...]] = ()
KEPT: Final = 5
TENS: Final = 10
MODEL_COUNT: Final = 256
POWER_DROP: Final = 30
POWER_SPAN: Final = 60
TORQUE_DROP: Final = 50
TORQUE_SPAN: Final = 100
CAP: Final = 0xFFFF
PREFIX: Final = "4900000"
CATEGORY_TEXT: Final[dict[str, Pair]] = {
    "FORMULA": ("Formula car", "フォーミュラ"),
    "K-CAR": ("Kei car", "けいじどうしゃ"),
    "NORMAL": ("Car", "ふつうしゃ"),
    "TRUCK": ("Truck", "トラック"),
    "SPECIAL": ("Special car", "スペシャル"),
}
TORQUE_HEADING: Final[Pair] = ("Torque", "トルク")

type Digits = tuple[int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class Reading:
    """A car as the game builds it from a code."""

    model: int
    power: int
    torque: int
    weight: int


def _tuned(base: int, drop: int, raised: int) -> int:
    """A number less its drop plus what the digits raise it by, held at the drop from below."""
    if base < drop:
        return drop
    return min(base - drop + raised, CAP)


def reading_of(kept: Digits) -> Reading:
    """The car five kept digits give."""
    e0, e1, e2, e3, e4 = kept
    x, y = TENS * e0 + e1, TENS * e3 + e4
    model = ((x + 1) * y - 1) % MODEL_COUNT
    _, power, torque, weight = MODELS[model]
    raised_power = (e2 + 1) * (TENS * e0 + e3 + 1) % POWER_SPAN
    raised_torque = (e2 + 1) * (TENS * e1 + e4 + 1) % TORQUE_SPAN
    return Reading(
        model,
        _tuned(power, POWER_DROP, raised_power),
        _tuned(torque, TORQUE_DROP, raised_torque),
        weight,
    )


def read_kattobi(code: str) -> Reading:
    """A code as the game reads it: its last five digits make the car."""
    digits = tuple(int(character) for character in validate_barcode(code)[-KEPT:])
    e0, e1, e2, e3, e4 = digits
    return reading_of((e0, e1, e2, e3, e4))


def decode_kattobi(code: str) -> DatachCard:
    """A barcode as Kattobi Road reads it: the car, its power and weight, and its torque."""
    code = validate_barcode(code)
    reading = read_kattobi(code)
    stats = (GameStat(POWER_KEY, reading.power), GameStat(WEIGHT_KEY, reading.weight))
    return DatachCard(code, Device.KATTOBI, GameKind.UNIT, reading.model, stats, (reading.torque,))


@cache
def _strongest_digits() -> dict[int, Digits]:
    """For each model, the five digits giving it the most power, then the most torque."""
    readings = [
        (reading_of((e0, e1, e2, e3, e4)), (e0, e1, e2, e3, e4))
        for e0, e1, e2, e3, e4 in product(range(TENS), repeat=KEPT)
    ]
    ranked = sorted(readings, key=lambda pair: (pair[0].model, _rank(pair[0])))
    return {reading.model: kept for reading, kept in ranked}


def code_for(kept: Digits) -> str:
    """An EAN-13 ending in these five digits, the eighth digit chosen so the last checks."""
    e0, e1, e2, e3, e4 = kept
    tail = f"{e0}{e1}{e2}{e3}"
    body = next(
        f"{PREFIX}{digit}{tail}"
        for digit in range(TENS)
        if expected_check_digit(f"{PREFIX}{digit}{tail}") == e4
    )
    return body + str(e4)


def build_kattobi(order: GameOrder) -> DatachCard | None:
    """The car ordered at the most power its codes give, the strongest car when none is named."""
    if order.ident is None:
        return strongest_kattobi()
    kept = _strongest_digits().get(order.ident)
    if kept is None:
        return None
    return decode_kattobi(code_for(kept))


def strongest_kattobi() -> DatachCard:
    """The car with the most power any code gives, then the most torque."""
    digits = _strongest_digits()
    model = max(digits, key=lambda ident: _rank(reading_of(digits[ident])))
    card = decode_kattobi(code_for(digits[model]))
    return required(card, "no Kattobi Road code could be found")


def _rank(reading: Reading) -> tuple[int, int]:
    """How a car ranks: power first, then torque."""
    return reading.power, reading.torque


def kattobi_entries() -> tuple[GameEntry, ...]:
    """Every car the game keeps, in its own order."""
    return tuple(
        GameEntry(model, GameKind.UNIT, ENGLISH[model], NAMES[model])
        for model in range(MODEL_COUNT)
    )


def kattobi_named(typed: str) -> int:
    """A car typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and int(text) < MODEL_COUNT:
        return int(text)
    for model in range(MODEL_COUNT):
        if text.casefold() == ENGLISH[model].casefold() or text == NAMES[model]:
            return model
    message = f"no Kattobi Road car named {typed!r}"
    raise ValueError(message)


def kattobi_text(card: DatachCard) -> CardText:
    """The car's name and category, then its torque."""
    (torque,) = card.traits
    category = CATEGORIES[MODELS[card.ident][0]]
    shown = f"{torque // TENS}.{torque % TENS} kg-m"
    return CardText(
        (ENGLISH[card.ident], NAMES[card.ident]),
        CATEGORY_TEXT[category],
        TORQUE_HEADING,
        (shown, shown),
    )
