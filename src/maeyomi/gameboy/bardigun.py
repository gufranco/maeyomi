"""Barcode Taisen Bardigun, Tamsoft 1998: a Game Boy game with its own reader that hatches eggs.

The rule is the game's own, followed through bank 4 $6B26 after a scan and
checked against every code it hatched in MAME. In an EAN-13 the eleventh digit,
1 to 7, picks one of seven tables of ten creatures and the check digit the
creature; 0, 8 and 9 hatch at random. An EAN-8 code is read the same way with
its third digit as the table and its first as the creature. A creature hatches
with the four numbers and HP its record in bank $0D gives it.
"""

from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat, required
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.check_digit import EAN_8_LENGTH, EAN_13_LENGTH, expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.gameboy.bardigun_tables import ENGLISH, NAMES, SPECIES_TABLES, STARTS
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said

TILE_KEYS: Final = ("DPW", "DSM", "DTG", "DSD", "DHP")
STAT_KEYS: Final[tuple[str, ...]] = ()
PLACES: Final = {EAN_13_LENGTH: (10, 12), EAN_8_LENGTH: (2, 0)}
"""Where each length keeps the digit that picks the table and the one that picks the creature."""
DIGITS: Final = 10
PREFIX: Final = "4900000000"
HP_PLACE: Final = 4
RANDOM_EGG: Final = len(NAMES)
RANDOM_NAME: Final[Pair] = ("A random Barloid", "なにが うまれるか わからない")
RANDOM_DETAIL: Final[Pair] = (
    "The digit that picks the table is 0, 8 or 9, so the egg hatches at random",
    "テーブルを えらぶ けたが 0、8、9 なので なにが うまれるかは ランダム",
)
START_HEADING: Final[Pair] = ("Hatches with", "うまれた ときの つよさ")
NO_START: Final[Pair] = ("", "")


def _hatched(code: str) -> int:
    """The creature a valid code hatches, or RANDOM_EGG when it hatches at random."""
    table_place, creature_place = PLACES[len(code)]
    table = SPECIES_TABLES.get(int(code[table_place]))
    return RANDOM_EGG if table is None else table[int(code[creature_place])]


def _card(code: str, species: int) -> DatachCard:
    """A card for what the code hatches, carrying the creature's starting numbers."""
    if species == RANDOM_EGG:
        return DatachCard(code, Device.BARDIGUN, GameKind.HIDDEN, RANDOM_EGG)
    stats = tuple(
        GameStat(key, value) for key, value in zip(TILE_KEYS, STARTS[species], strict=True)
    )
    return DatachCard(code, Device.BARDIGUN, GameKind.FIGHTER, species, stats)


def decode_bardigun(code: str) -> DatachCard:
    """A barcode as Bardigun hatches it."""
    valid = validate_barcode(code)
    return _card(valid, _hatched(valid))


def code_for(species: int) -> str | None:
    """The first EAN-13 that hatches this creature, or None when no table holds it."""
    places = (
        (digit, last)
        for digit, table in SPECIES_TABLES.items()
        for last, held in enumerate(table)
        if held == species
    )
    found = next(places, None)
    if found is None:
        return None
    digit, last = found
    body = next(
        candidate
        for candidate in (f"{PREFIX}{digit}{twelfth}" for twelfth in range(DIGITS))
        if expected_check_digit(candidate) == last
    )
    return f"{body}{last}"


def build_bardigun(order: GameOrder) -> DatachCard | None:
    """A code that hatches the creature ordered, or the strongest when none is named."""
    if order.ident is None:
        return strongest_bardigun()
    code = code_for(order.ident)
    return None if code is None else decode_bardigun(code)


def _reachable() -> tuple[int, ...]:
    """Every creature some table holds, in the game's own order."""
    return tuple(sorted({species for table in SPECIES_TABLES.values() for species in table}))


def _strength(species: int) -> tuple[int, int]:
    """How the strongest is ranked: starting HP, then the four numbers together."""
    start = STARTS[species]
    return start[HP_PLACE], sum(start[:HP_PLACE])


def strongest_bardigun() -> DatachCard:
    """The creature that hatches with the most HP, then the most in its four numbers."""
    anything = Constraint.anything()
    best = max(_reachable(), key=_strength)
    order = GameOrder(best, (anything, anything, anything))
    return required(build_bardigun(order), "no Bardigun code could be found")


def bardigun_entries() -> tuple[GameEntry, ...]:
    """Every creature a barcode can be sure to hatch."""
    return tuple(
        GameEntry(species, GameKind.FIGHTER, ENGLISH[species], NAMES[species])
        for species in _reachable()
    )


def bardigun_named(typed: str) -> int:
    """A creature typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and int(text) < len(NAMES):
        return int(text)
    for species, (english, japanese) in enumerate(zip(ENGLISH, NAMES, strict=True)):
        if text.casefold() == english.casefold() or text == japanese:
            return species
    message = Said(
        f"no Bardigun creature named {typed!r}",
        f"バーディガンに {typed!r} という バーロイドは いない",
    )
    raise ValueError(message)


def bardigun_text(card: DatachCard) -> CardText:
    """The creature's name and number, then what it hatches with."""
    if card.ident == RANDOM_EGG:
        return CardText(RANDOM_NAME, RANDOM_DETAIL, START_HEADING, NO_START)
    power, smarts, toughness, speed, hp = STARTS[card.ident]
    return CardText(
        (ENGLISH[card.ident], NAMES[card.ident]),
        (f"Barloid number {card.ident}", f"バーロイド {card.ident}ばん"),
        START_HEADING,
        (
            f"Power {power}, smarts {smarts}, toughness {toughness}, speed {speed}, HP {hp}",
            f"ちから {power}、あたま {smarts}、じょうぶ {toughness}、はやさ {speed}、HP {hp}",
        ),
    )
