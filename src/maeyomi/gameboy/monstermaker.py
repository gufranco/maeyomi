"""Monster Maker: Barcode Saga, Namco 1993: a Barcode Boy game that reads a party of heroes.

The rule is the game's own, followed through its code after a scan and checked
against every code it read in MAME. It reads a card two ways. Forming the party
it gives one of seventeen heroes at level 1; later in the game the same card
gives one of thirty-five characters, a hero or one of eighteen others, and a hero comes
at a level the digits fix.

A code starting with 9 names the character by `d2 + d3 + d4`, halved from 18
up. Any other code names it by `d5 * 10 + d7`, brought under 18 by taking 17
away forming the party, and under 36 by taking 35 away later. A zero moves the
reading one digit on, and past the last digit the game reads the zeros after
it and then its own roster, whose first byte is the first character's class.
Later, the level is `3 * (d0 + d2 + d4) + 1` in its low four bits, a zero read
as one and anything from ten up halved.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameOption, GamePick, GameStat, required
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.gameboy.monstermaker_names import CHARACTER_ENGLISH, CLASS_ENGLISH
from maeyomi.gameboy.monstermaker_tables import (
    CLASS_NAMES,
    CLASSES,
    HERO_STATS,
    MONSTER_STATS,
    NAMES,
)
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said

HP_KEY: Final = "GHP"
MP_KEY: Final = "BMP"
AP_KEY: Final = "AP"
DP_KEY: Final = "GDP"
STAT_KEYS: Final[tuple[str, ...]] = ()
LATER_KEY: Final = "later"
HEROES: Final = 17
CHARACTERS: Final = 35
LEVELS: Final = 9
NINE: Final = 9
NAME_FIRST: Final = 5
SUM_DIGITS: Final = (2, 3, 4)
LEVEL_DIGITS: Final = (0, 2, 4)
HALVE_FROM: Final = 18
FIVE_BITS: Final = 0x1F
LOW_BITS: Final = 0x0F
HALVE_LEVEL_FROM: Final = 10
ROSTER: Final = 0x9C
TENS: Final = 10
SLOT: Final = 100
LAST_BODY_DIGIT: Final = 8
MAX_NAME: Final = 99
LATER_HEADING: Final[Pair] = ("Later in the game", "ゲーム の とちゅう で")
LATER_PICK: Final[Pair] = ("Later in the game", "ゲーム の とちゅう")

type Stats = tuple[int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class Reading:
    """What the game makes of a code: the party hero, and the character it gives later."""

    party: int
    party_class: int
    later: int
    later_level: int
    later_class: int


def memory(code: str) -> list[int]:
    """The digits as the game holds them, then the zeros and the roster byte it can read on into."""
    digits = [int(character) for character in code]
    return [*digits, *[0] * (ROSTER - len(digits)), CLASSES[0]]


def _named_by_nine(held: list[int]) -> int:
    """The character a code starting with 9 names, the same forming the party and later."""
    value = sum(held[index] for index in SUM_DIGITS) & FIVE_BITS
    if value >= HALVE_FROM:
        value >>= 1
    return value or next(digit for digit in held[NAME_FIRST:] if digit)


def _named_by_pair(held: list[int], limit: int) -> int:
    """The character any other code names, brought under the limit plus one."""
    values = (
        _under(held[position] * TENS + held[position + 2], limit)
        for position in range(NAME_FIRST, ROSTER - 1)
    )
    return next(value for value in values if value)


def _under(value: int, limit: int) -> int:
    """A value brought to the limit or below by taking the limit away."""
    while value > limit:
        value -= limit
    return value


def _named(held: list[int], limit: int) -> int:
    """The character a code names, reading up to the limit."""
    if held[0] == NINE:
        return _named_by_nine(held)
    return _named_by_pair(held, limit)


def level_of(held: list[int]) -> int:
    """The level a hero comes at later in the game."""
    level = (3 * sum(held[index] for index in LEVEL_DIGITS) + 1) & LOW_BITS
    level = level or 1
    return level >> 1 if level >= HALVE_LEVEL_FROM else level


def read_monster_maker(code: str) -> Reading:
    """Both readings of a code, as the game makes them."""
    held = memory(validate_barcode(code))
    party = _named(held, HEROES)
    later = _named(held, CHARACTERS)
    return Reading(party, CLASSES[party - 1], later, level_of(held), CLASSES[later - 1])


def stats_of(ident: int, level: int) -> Stats:
    """A character's move, DP, MP, AP and HP: a hero's at its level, anyone else's fixed."""
    if ident <= HEROES:
        return HERO_STATS[ident - 1][level - 1]
    return MONSTER_STATS[ident - HEROES - 1]


def decode_monster_maker(code: str) -> DatachCard:
    """A barcode as Monster Maker reads it: the party hero first, then what it gives later."""
    code = validate_barcode(code)
    reading = read_monster_maker(code)
    move, dp, mp, ap, hp = stats_of(reading.party, 1)
    stats = (GameStat(HP_KEY, hp), GameStat(MP_KEY, mp), GameStat(AP_KEY, ap), GameStat(DP_KEY, dp))
    return DatachCard(
        code,
        Device.MONSTER_MAKER,
        GameKind.FIGHTER,
        reading.party,
        stats,
        (move, reading.later, reading.later_level),
    )


def later_value(card: DatachCard) -> int:
    """The later reading as the pick names it: the character times 100, plus a hero's level."""
    _, later, level = card.traits
    return later * SLOT + (level if later <= HEROES else 0)


def _later_names(party: int) -> list[int]:
    """Every value a code for this party hero can name, which fixes what it gives later."""
    return list(range(party, MAX_NAME + 1, HEROES))


def _later_of(value: int) -> int:
    """The character a named value gives later in the game."""
    return _under(value, CHARACTERS)


def monster_maker_picks(ident: int) -> tuple[GamePick, ...]:
    """What a hero's card can give later: heroes at each level, then the others."""
    later = sorted({_later_of(value) for value in _later_names(ident)})
    options = [
        _option(character * SLOT + level, character, level)
        for character in later
        for level in (range(1, LEVELS + 1) if character <= HEROES else (0,))
    ]
    return (GamePick(LATER_KEY, *LATER_PICK, tuple(options)),)


def _option(value: int, character: int, level: int) -> GameOption:
    """One later reading, named in both languages."""
    english, japanese = CHARACTER_ENGLISH[character - 1], NAMES[character - 1]
    if level:
        return GameOption(value, f"{english}, level {level}", f"{japanese} レベル{level}")
    return GameOption(value, english, japanese)


def build_monster_maker(order: GameOrder) -> DatachCard | None:
    """A code the game reads as the hero ordered, giving the later reading picked, or None.

    With no later reading picked, the hero comes back later at level 9, and with
    no hero ordered the strongest one stands in.
    """
    if order.ident is None:
        return strongest_monster_maker()
    if not 1 <= order.ident <= HEROES:
        return None
    wanted = dict(order.picks).get(LATER_KEY, order.ident * SLOT + LEVELS)
    character, level = divmod(wanted, SLOT)
    named = next(
        (value for value in _later_names(order.ident) if _later_of(value) == character), None
    )
    sums = next((total for total in range(3 * NINE) if _level_for(total) == (level or 1)), None)
    if named is None or sums is None:
        return None
    return decode_monster_maker(_code(named, sums))


def _level_for(total: int) -> int:
    """The level a code whose level digits add up to this total gives."""
    return level_of([total, 0, 0, 0, 0])


def _code(named: int, total: int) -> str:
    """A code not starting with 9 that names this value, with level digits adding to the total."""
    first = min(total, LAST_BODY_DIGIT)
    third = min(total - first, NINE)
    fifth = total - first - third
    tens, units = divmod(named, TENS)
    body = f"{first}0{third}0{fifth}{tens}0{units}0000"
    return body + str(expected_check_digit(body))


def strongest_monster_maker() -> DatachCard:
    """Lorian at level 9 later in the game, whose HP 460 no other hero reaches."""
    strongest = max(range(1, HEROES + 1), key=lambda hero: _power(stats_of(hero, LEVELS)))
    anything = Constraint.anything()
    card = build_monster_maker(GameOrder(strongest, (anything, anything, anything)))
    return required(card, "no Monster Maker code could be found")


def _power(stats: Stats) -> tuple[int, int, int]:
    """How a hero ranks: HP first, then AP and MP together, then DP."""
    _, dp, mp, ap, hp = stats
    return hp, ap + mp, dp


def monster_maker_entries() -> tuple[GameEntry, ...]:
    """Every hero a card gives forming the party, in the game's own order."""
    return tuple(
        GameEntry(ident, GameKind.FIGHTER, CHARACTER_ENGLISH[ident - 1], NAMES[ident - 1])
        for ident in range(1, HEROES + 1)
    )


def monster_maker_named(typed: str) -> int:
    """A hero typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and 1 <= int(text) <= HEROES:
        return int(text)
    for ident in range(1, HEROES + 1):
        if text.casefold() == CHARACTER_ENGLISH[ident - 1].casefold() or text == NAMES[ident - 1]:
            return ident
    message = Said(
        f"no Monster Maker hero named {typed!r}",
        f"モンスターメーカーに {typed!r} という ゆうしゃは ない",
    )
    raise ValueError(message)


def monster_maker_text(card: DatachCard) -> CardText:
    """The party hero with its class and move, then what the card gives later."""
    move, later, level = card.traits
    klass = CLASSES[card.ident - 1]
    return CardText(
        (CHARACTER_ENGLISH[card.ident - 1], NAMES[card.ident - 1]),
        (
            f"{CLASS_ENGLISH[klass]}, move {move}",
            f"{CLASS_NAMES[klass]}・ムーブ {move}",
        ),
        LATER_HEADING,
        _later_text(later, level),
    )


def _later_text(character: int, level: int) -> Pair:
    """A later reading with its numbers, a hero's with its level."""
    move, dp, mp, ap, hp = stats_of(character, level)
    english, japanese = CHARACTER_ENGLISH[character - 1], NAMES[character - 1]
    if character <= HEROES:
        english, japanese = f"{english}, level {level}", f"{japanese} レベル{level}"
    return (
        f"{english}: HP {hp}, AP {ap}, MP {mp}, DP {dp}, move {move}",
        f"{japanese}: HP {hp} AP {ap} MP {mp} DP {dp} ムーブ {move}",
    )
