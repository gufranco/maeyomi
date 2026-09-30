"""Family Jockey 2, Namco 1993: a Barcode Boy horse racing game that reads a card as a horse.

The rule is the game's own, followed through its code after a scan and checked
against every code it read in MAME, in each of the three menus that read a card:
racehorse, mare and stallion. The digits are taken right-aligned into thirteen
places, zeros before a short code. With s the sum of all thirteen mod 10, the
menu's key table gives a row of seven keys; digits 6 to 11 each plus their key,
mod 10, are the six numbers, read from digit 11 down as speed, stamina, guts,
jump, turbo and type. A code whose first ten places are one of seven Namco box
codes also earns the bonus the game names for it.
"""

from dataclasses import dataclass
from itertools import product
from typing import Final

from maeyomi.datach.game_card import (
    DatachCard,
    GameKind,
    GameOption,
    GamePick,
    GameStat,
    required,
)
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.gameboy.famjock2_names import BONUSES, KINDS, SHORT, STATS
from maeyomi.gameboy.famjock2_tables import BOXES, MARE_KEYS, RACEHORSE_KEYS, STALLION_KEYS
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said

RACEHORSE: Final = 0
MARE: Final = 1
STALLION: Final = 2
KEY_TABLES: Final = (RACEHORSE_KEYS, MARE_KEYS, STALLION_KEYS)
TILE_KEYS: Final = ("HSP", "HST", "HGT", "HJP", "HTB", "HTP")
STAT_PICKS: Final = ("speed", "stamina", "guts", "jump", "turbo", "type")
STAT_KEYS: Final[tuple[str, ...]] = ()
PLACES: Final = 13
FIRST_STAT: Final = 6
STAT_COUNT: Final = 6
BOX_PLACES: Final = 10
DIGITS: Final = 10
BONUS_RAISES: Final = {1: 1, 2: 0, 3: 4, 4: 2, 5: 5, 6: 3}
"""Which of the six numbers each Namco box raises by two, per bank 2 $4119."""
EVERY_NUMBER: Final = 7
BONUS_CAP: Final = 10
BOX_TAILS: Final = 100
TOP: Final = 9
PREFIX: Final = "49"
FREE: Final = 4
OTHER_HEADING: Final[Pair] = ("In the other menus", "ほかの メニューでは")

type Stats = tuple[int, int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class Horse:
    """A horse as one menu builds it: its six numbers and any Namco box bonus, 1 to 7."""

    stats: Stats
    bonus: int


def _places(code: str) -> list[int]:
    """The digits right-aligned into thirteen places, zeros before a short code."""
    digits = [int(character) for character in code]
    return [*[0] * (PLACES - len(digits)), *digits]


def _stats(places: list[int], kind: int) -> Stats:
    """The six numbers one menu's key table makes from the places."""
    keys = KEY_TABLES[kind][sum(places) % DIGITS]
    shifted = [
        (places[FIRST_STAT + index] + keys[1 + index]) % DIGITS for index in range(STAT_COUNT)
    ]
    speed, stamina, guts, jump, turbo, kind_of = reversed(shifted)
    return speed, stamina, guts, jump, turbo, kind_of


def _bonus(places: list[int]) -> int:
    """Which Namco box code the first ten places are, 1 to 7, or 0."""
    head = "".join(map(str, places[:BOX_PLACES]))
    return next((index + 1 for index, box in enumerate(BOXES) if head == box), 0)


def read_famjock2(code: str, kind: int) -> Horse:
    """A code as the game reads it in one menu."""
    places = _places(validate_barcode(code))
    return Horse(_stats(places, kind), _bonus(places))


def _card(code: str, kind: int) -> DatachCard:
    """A card for one menu, carrying the other two readings beside its own."""
    horses = [read_famjock2(code, menu) for menu in range(len(KINDS))]
    stats = tuple(
        GameStat(key, value) for key, value in zip(TILE_KEYS, horses[kind].stats, strict=True)
    )
    others = [value for menu, horse in enumerate(horses) if menu != kind for value in horse.stats]
    return DatachCard(
        code, Device.FAMJOCK2, GameKind.FIGHTER, kind, stats, (horses[kind].bonus, *others)
    )


def decode_famjock2(code: str) -> DatachCard:
    """A barcode as Family Jockey 2 reads it in the racehorse menu, with its other two readings."""
    return _card(validate_barcode(code), RACEHORSE)


def famjock2_picks(_ident: int) -> tuple[GamePick, ...]:
    """The six numbers a horse is ordered with, each from 0 to 9."""
    options = tuple(GameOption(value, str(value), str(value)) for value in range(DIGITS))
    return tuple(
        GamePick(key, english, japanese, options)
        for key, (english, japanese) in zip(STAT_PICKS, STATS, strict=True)
    )


def build_famjock2(order: GameOrder) -> DatachCard | None:
    """A code the menu ordered reads as the six numbers picked, 9 for any left out."""
    if order.ident is None:
        return strongest_famjock2()
    if order.ident not in range(len(KINDS)):
        return None
    picked = dict(order.picks)
    wanted = tuple(picked.get(key, TOP) for key in STAT_PICKS)
    return _card(code_for(order.ident, wanted), order.ident)


def code_for(kind: int, wanted: tuple[int, ...]) -> str:
    """An EAN-13 the menu reads as these numbers, with no Namco box bonus."""
    candidates = (
        _candidate(kind, wanted, row, free)
        for row in range(DIGITS)
        for free in product(range(DIGITS), repeat=FREE)
    )
    return next(code for code in candidates if code is not None)


def _candidate(kind: int, wanted: tuple[int, ...], row: int, free: tuple[int, ...]) -> str | None:
    """The code with these free digits for this key row, when its digit sum picks that row."""
    keys = KEY_TABLES[kind][row]
    stat_places = [
        (value - keys[1 + index]) % DIGITS for index, value in enumerate(reversed(wanted))
    ]
    body = PREFIX + "".join(map(str, (*free, *stat_places)))
    code = body + str(expected_check_digit(body))
    places = _places(code)
    if sum(places) % DIGITS != row or _bonus(places):
        return None
    return code


def strongest_famjock2() -> DatachCard:
    """A racehorse with 9 in every number."""
    anything = Constraint.anything()
    card = build_famjock2(GameOrder(RACEHORSE, (anything, anything, anything)))
    return required(card, "no Family Jockey 2 code could be found")


def famjock2_entries() -> tuple[GameEntry, ...]:
    """The three menus a card is read in."""
    return tuple(
        GameEntry(kind, GameKind.FIGHTER, english, japanese)
        for kind, (english, japanese) in enumerate(KINDS)
    )


def famjock2_named(typed: str) -> int:
    """A menu typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and int(text) < len(KINDS):
        return int(text)
    for kind, (english, japanese) in enumerate(KINDS):
        if text.casefold() == english.casefold() or text == japanese:
            return kind
    message = Said(
        f"no Family Jockey 2 horse kind named {typed!r}",
        f"ファミリージョッキー2に {typed!r} という うまの しゅるいは ない",
    )
    raise ValueError(message)


def famjock2_text(card: DatachCard) -> CardText:
    """The menu the card was read in or its bonus, then its readings in the other two menus."""
    bonus, *others = card.traits
    english, japanese = KINDS[card.ident]
    detail = (
        BONUSES[bonus - 1]
        if bonus
        else (f"Read in the {english.lower()} menu", f"{japanese}の メニューで よむ")
    )
    menus = [menu for menu in range(len(KINDS)) if menu != card.ident]
    readings = [
        (
            KINDS[menu],
            " ".join(
                f"{short}{value}"
                for short, value in zip(
                    SHORT, others[index * STAT_COUNT : (index + 1) * STAT_COUNT], strict=True
                )
            ),
        )
        for index, menu in enumerate(menus)
    ]
    (first, first_stats), (second, second_stats) = readings
    power = (
        f"{first[0]} {first_stats}, {second[0].lower()} {second_stats}",
        f"{first[1]} {first_stats}、{second[1]} {second_stats}",
    )
    return CardText(KINDS[card.ident], detail, OTHER_HEADING, power)


def after_bonus(stats: Stats, bonus: int) -> Stats:
    """The six numbers once the player confirms the horse, per bank 2 $4114.

    Each box raises its number by two and the Barcode Boy's own box every number
    by one, each step held at 10, as the game did in MAME.
    """
    speed, stamina, guts, jump, turbo, kind = (
        min(BONUS_CAP, value + (bonus == EVERY_NUMBER) + 2 * (BONUS_RAISES.get(bonus) == place))
        for place, value in enumerate(stats)
    )
    return speed, stamina, guts, jump, turbo, kind


def strongest_boxed() -> DatachCard:
    """The racehorse a Namco box code makes strongest once its bonus lands, the only way past 9."""
    codes = (
        box + f"{tail:02d}" + str(expected_check_digit(box + f"{tail:02d}"))
        for box, tail in product(BOXES, range(BOX_TAILS))
    )
    boxed = [(code, read_famjock2(code, RACEHORSE)) for code in codes]
    code, _ = max(
        ((code, horse) for code, horse in boxed if horse.bonus),
        key=lambda pair: (sum(after_bonus(*_horse(pair[1]))), min(after_bonus(*_horse(pair[1])))),
    )
    return decode_famjock2(code)


def _horse(horse: Horse) -> tuple[Stats, int]:
    """A horse's numbers and its bonus, as `after_bonus` takes them."""
    return horse.stats, horse.bonus
