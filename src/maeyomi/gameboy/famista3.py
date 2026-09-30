"""Famista 3, Namco 1993: a Barcode Boy baseball game that reads a card as a rookie player.

The rule is the game's own, followed through its code after a scan and checked
against every code it read in MAME. A 13-digit code makes a pitcher when
d2 + d9 < 8 and a batter otherwise; d12 picks one of the game's groups of
players and a step byte, sum((da + db) >> 1 * w) for the pairs (d0, d5),
(d4, d8), (d3, d11), (d1, d10) and (d6, d7) weighted 16, 8, 4, 2 and 1, picks
the player in it. An 8-digit code uses d0 + d3 < 8, d7, and the digits
d4, d1, d2, d6 and d5 whole. The game copies the player from its own data, so
every card is a player it already knows, named Rookie.
"""

from dataclasses import dataclass
from functools import cache
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
from maeyomi.gameboy.famista3_tables import BATTER_GROUPS, BATTERS, PITCHER_GROUPS, PITCHERS
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said

HOMERS_KEY: Final = "FHR"
RUN_SPEED_KEY: Final = "FSP"
PITCH_SPEED_KEY: Final = "FKM"
STAMINA_KEY: Final = "FST"
STAT_KEYS: Final[tuple[str, ...]] = ()
PICK_KEY: Final = "player"
BATTER: Final = 0
PITCHER: Final = 1
KINDS: Final[tuple[Pair, ...]] = (("Batter", "バッター"), ("Pitcher", "ピッチャー"))
EAN_8: Final = 8
PAIRS: Final = ((0, 5), (4, 8), (3, 11), (1, 10), (6, 7))
EIGHT_DIGITS: Final = (4, 1, 2, 6, 5)
WEIGHTS: Final = (16, 8, 4, 2, 1)
KIND_DIGITS: Final = (2, 9)
EIGHT_KIND_DIGITS: Final = (0, 3)
PITCHER_BELOW: Final = 8
LAST: Final = 12
EIGHT_LAST: Final = 7
BYTE: Final = 0xFF
STEPS: Final = 256
DIGITS: Final = 10
SWITCH: Final = 0x80
LEFT: Final = 0x01
HUNDREDTHS: Final = 100
PITCHER_KIND_DIGITS: Final = ((0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (3, 0))
BATTER_KIND_DIGITS: Final = ((9, 9), (8, 9), (9, 8), (8, 8), (7, 9), (9, 7))
AVERAGE_HEADING: Final[Pair] = ("Batting average", "打率")
ERA_HEADING: Final[Pair] = ("ERA", "防御率")
ROOKIE: Final[Pair] = ("Rookie", "ルーキー")
PICK_NAME: Final[Pair] = ("Player", "せんしゅ")

type Player = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Reading:
    """A player as the game copies it: kind, side, the three numbers, and where it came from."""

    kind: int
    side: int
    first: int
    second: int
    third: int
    group: int
    step: int


def _placement(digits: list[int]) -> tuple[int, int, int]:
    """The kind, the digit that picks the group, and the step a code gives."""
    if len(digits) == EAN_8:
        kind_sum = sum(digits[index] for index in EIGHT_KIND_DIGITS)
        step = sum(
            digits[index] * weight for index, weight in zip(EIGHT_DIGITS, WEIGHTS, strict=True)
        )
        return _kind(kind_sum), digits[EIGHT_LAST], step & BYTE
    kind_sum = sum(digits[index] for index in KIND_DIGITS)
    step = sum(
        ((digits[first] + digits[second]) >> 1) * weight
        for (first, second), weight in zip(PAIRS, WEIGHTS, strict=True)
    )
    return _kind(kind_sum), digits[LAST], step & BYTE


def _kind(kind_sum: int) -> int:
    """A pitcher under the threshold, a batter otherwise."""
    return PITCHER if kind_sum < PITCHER_BELOW else BATTER


def player_at(kind: int, group: int, step: int) -> Player:
    """The player a kind, group and step point at."""
    return (PITCHERS if kind == PITCHER else BATTERS)[group][step]


def read_famista3(code: str) -> Reading:
    """A code as the game reads it."""
    digits = [int(character) for character in validate_barcode(code)]
    kind, last, step = _placement(digits)
    group = (PITCHER_GROUPS if kind == PITCHER else BATTER_GROUPS)[last]
    side, first, second, third = player_at(kind, group, step)
    return Reading(kind, side, first, second, third, group, step)


def decode_famista3(code: str) -> DatachCard:
    """A barcode as Famista 3 reads it: a batter or pitcher and the numbers the game shows."""
    code = validate_barcode(code)
    reading = read_famista3(code)
    keys = (
        (PITCH_SPEED_KEY, STAMINA_KEY) if reading.kind == PITCHER else (HOMERS_KEY, RUN_SPEED_KEY)
    )
    stats = (GameStat(keys[0], reading.second), GameStat(keys[1], reading.third))
    traits = (reading.side, reading.first, reading.group, reading.step)
    return DatachCard(code, Device.FAMISTA3, GameKind.PLAYER, reading.kind, stats, traits)


def pick_value(card: DatachCard) -> int:
    """Where a card's player sits, as the pick names it: its group times 256 plus its step."""
    _, _, group, step = card.traits
    return group * STEPS + step


def _strength(kind: int, player: Player) -> tuple[int, int, int]:
    """How a player ranks: a batter by home runs, then average; a pitcher by ERA, then speed."""
    _, first, second, third = player
    if kind == PITCHER:
        return -first, second, third
    return second, first, third


@cache
def _places(kind: int) -> tuple[int, ...]:
    """One place for each distinct player of a kind, strongest first."""
    groups = PITCHERS if kind == PITCHER else BATTERS
    first_seen = {
        groups[group][step]: group * STEPS + step
        for group in reversed(range(len(groups)))
        for step in reversed(range(STEPS))
    }
    ranked = sorted(first_seen.items(), key=lambda pair: _strength(kind, pair[0]), reverse=True)
    return tuple(place for _, place in ranked)


def famista3_picks(ident: int) -> tuple[GamePick, ...]:
    """Every distinct player of a kind a code can give, strongest first."""
    options = tuple(_option(ident, place) for place in _places(ident))
    return (GamePick(PICK_KEY, *PICK_NAME, options),)


def _option(kind: int, place: int) -> GameOption:
    """One player, named by its numbers in both languages."""
    group, step = divmod(place, STEPS)
    side, first, second, third = player_at(kind, group, step)
    english, japanese = _side_text(kind, side)
    if kind == PITCHER:
        era = _era(first)
        return GameOption(
            place,
            f"{english}, ERA {era}, {second} km/h, stamina {third}",
            f"{japanese} 防{era} {second}km/h スタミナ{third}",
        )
    average = _average(first)
    return GameOption(
        place,
        f"{english}, {average}, {second} home runs, speed {third}",
        f"{japanese} {average} 本塁打{second} 走力{third}",
    )


def build_famista3(order: GameOrder) -> DatachCard | None:
    """A code the game reads as the player picked, the strongest of its kind when none is."""
    if order.ident is None:
        return strongest_famista3()
    if order.ident not in (BATTER, PITCHER):
        return None
    place = dict(order.picks).get(PICK_KEY, _places(order.ident)[0])
    group, step = divmod(place, STEPS)
    groups = PITCHER_GROUPS if order.ident == PITCHER else BATTER_GROUPS
    if group not in groups:
        return None
    return decode_famista3(code_for(order.ident, group, step))


@cache
def _halves() -> dict[int, tuple[int, ...]]:
    """For each step, the five pair halves giving it that come first in counting order."""
    return {
        sum(half * weight for half, weight in zip(halves, WEIGHTS, strict=True)) & BYTE: halves
        for halves in reversed(list(product(range(DIGITS), repeat=len(WEIGHTS))))
    }


def code_for(kind: int, group: int, step: int) -> str:
    """An EAN-13 the game reads as this kind, group and step."""
    groups = PITCHER_GROUPS if kind == PITCHER else BATTER_GROUPS
    wanted = {digit for digit in range(DIGITS) if groups[digit] == group}
    kind_options = PITCHER_KIND_DIGITS if kind == PITCHER else BATTER_KIND_DIGITS
    pair_options = [_splits(half) for half in _halves()[step]]
    bodies = (
        _body(kind_digits, pairs) for kind_digits, *pairs in product(kind_options, *pair_options)
    )
    body = next(body for body in bodies if expected_check_digit(body) in wanted)
    return body + str(expected_check_digit(body))


def _splits(half: int) -> list[tuple[int, int]]:
    """The digit pairs whose sum halves to this value."""
    return [
        (first, total - first)
        for total in (2 * half, 2 * half + 1)
        for first in range(DIGITS)
        if 0 <= total - first < DIGITS
    ]


def _body(kind_digits: tuple[int, int], pairs: list[tuple[int, int]]) -> str:
    """The twelve digits before the check digit, placed where the game reads them."""
    placed = {
        **{
            index: value
            for (first, second), (low, high) in zip(PAIRS, pairs, strict=True)
            for index, value in ((first, low), (second, high))
        },
        **dict(zip(KIND_DIGITS, kind_digits, strict=True)),
    }
    return "".join(str(placed[index]) for index in range(LAST))


def strongest_famista3() -> DatachCard:
    """The batter with the most home runs any code gives, then the best average and speed."""
    anything = Constraint.anything()
    order = GameOrder(BATTER, (anything, anything, anything), ((PICK_KEY, _places(BATTER)[0]),))
    return required(build_famista3(order), "no Famista 3 code could be found")


def famista3_entries() -> tuple[GameEntry, ...]:
    """The two kinds of player a card can be."""
    return tuple(
        GameEntry(kind, GameKind.PLAYER, english, japanese)
        for kind, (english, japanese) in enumerate(KINDS)
    )


def famista3_named(typed: str) -> int:
    """A kind typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and int(text) < len(KINDS):
        return int(text)
    for kind, (english, japanese) in enumerate(KINDS):
        if text.casefold() == english.casefold() or text == japanese:
            return kind
    message = Said(
        f"no Famista 3 player kind named {typed!r}",
        f"ファミスタ3に {typed!r} という せんしゅの しゅるいは ない",
    )
    raise ValueError(message)


def famista3_text(card: DatachCard) -> CardText:
    """A rookie with its kind and side, then its average or ERA."""
    side, first, _, _ = card.traits
    english, japanese = _side_text(card.ident, side)
    kind_english, kind_japanese = KINDS[card.ident]
    detail = (f"{kind_english}, {english.lower()}", f"{kind_japanese}・{japanese}")
    if card.ident == PITCHER:
        era = _era(first)
        return CardText(ROOKIE, detail, ERA_HEADING, (era, era))
    average = _average(first)
    return CardText(ROOKIE, detail, AVERAGE_HEADING, (average, average))


def _side_text(kind: int, side: int) -> Pair:
    """Which hand a player uses, as the game prints it."""
    if kind == PITCHER:
        return ("Throws left", "左投げ") if side & LEFT else ("Throws right", "右投げ")
    if side & SWITCH:
        return "Switch hitter", "打席 両"
    return ("Bats left", "打席 左") if side & LEFT else ("Bats right", "打席 右")


def _average(thousandths: int) -> str:
    """A batting average as the screen shows it, .280."""
    return f".{thousandths:03d}"


def _era(hundredths: int) -> str:
    """An ERA as the screen shows it, 2.90."""
    return f"{hundredths // HUNDREDTHS}.{hundredths % HUNDREDTHS:02d}"
