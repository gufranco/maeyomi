"""Battle Space, Namco 1992: the game packed with the Barcode Boy, which reads a fighter.

The rule is the game's own, followed through its code after a scan and checked
against 668 codes it read in MAME. It builds thirteen new digits from the
barcode: four from `d[d[i] + 2] * (9, 7, 3, 3)[i] mod 10`, then `d4 + 1, d6, d8`
and `d5 + 1, d7, d9` with the first of each taken mod 10, then three from
`d[12 - d[i]] * (7, 3, 3) mod 10` for the last three digits. Those read as HP in
four digits, MP, AP and DP in three each, a zero read as one, and the screen
shows each times a hundred.

The class comes from where the four numbers sit against thresholds: one row
picks a second row, and the sixteen answers index a class table. The class
fixes the magic, one of three spell groups or none, and the special move.
"""

from collections.abc import Iterator
from itertools import product
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat, required
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.gameboy.battlespace_names import CLASS_ENGLISH, SPECIAL_ENGLISH, SPELL_ENGLISH
from maeyomi.gameboy.battlespace_tables import (
    CLASS_MAP,
    CLASS_NAMES,
    FIRST_THRESHOLDS,
    MAGIC_GROUPS,
    ROWS,
    SPECIAL_NAMES,
    SPECIALS,
    SPELL_NAMES,
    STEPS,
)
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said

HP_KEY: Final = "GHP"
MP_KEY: Final = "BMP"
AP_KEY: Final = "AP"
DP_KEY: Final = "GDP"
STAT_KEYS: Final = (HP_KEY, AP_KEY, DP_KEY)
UNIT: Final = 100
GROUPS: Final = (4, 3, 3, 3)
TOPS: Final = (9999, 999, 999, 999)
HP_WEIGHTS: Final = (9, 7, 3, 3)
DP_WEIGHTS: Final = (7, 3, 3)
DP_DIGITS: Final = (10, 11, 12)
INVERSE: Final = {1: 1, 3: 7, 7: 3, 9: 9}
DIGITS: Final = 10
LAST: Final = 12
SHIFT: Final = 2
MIDDLE_FIRST: Final = 4
BITS: Final = 4
BYTE: Final = 0xFF
SECOND_STEP: Final = 2
LOW_BITS: Final = 4
NO_SPECIAL: Final = -1
TAIL_FIRST: Final = 10
MAX_STEPS: Final = 3
EAN_13: Final = 13
MAX_ATTEMPTS: Final = 200_000
MAGIC_LETTERS: Final = {1: "C", 2: "M", 3: "CM"}
SPELLS: Final = {1: range(7), 2: range(7, 14), 3: range(14)}
SPECIAL_HEADING: Final[Pair] = ("Special", "とくしゅ")
SPELLS_HEADING: Final[Pair] = ("Spells", "じゅもん")
BOTH_HEADING: Final[Pair] = ("Special and spells", "とくしゅ と じゅもん")
EVERY_SPELL_GROUP: Final = 3
EVERY_SPELL: Final[Pair] = (
    f"All {len(SPELLS[EVERY_SPELL_GROUP])} spells",
    f"{len(SPELLS[EVERY_SPELL_GROUP])}しゅ すべて",
)
NONE: Final[Pair] = ("None", "なし")
NO_MAGIC: Final[Pair] = ("Fighter, no magic", "せんし・まほう なし")

type Stats = tuple[int, int, int, int]
type Band = tuple[int, int]


def scramble(digits: list[int]) -> list[int]:
    """The thirteen digits the game builds from the barcode's."""
    out = [digits[digits[i] + SHIFT] * weight % DIGITS for i, weight in enumerate(HP_WEIGHTS)]
    for start in (MIDDLE_FIRST, MIDDLE_FIRST + 1):
        out += [(digits[start] + 1) % DIGITS, digits[start + 2], digits[start + 4]]
    out += [
        digits[LAST - digits[i]] * w % DIGITS for i, w in zip(DP_DIGITS, DP_WEIGHTS, strict=True)
    ]
    return out


def stats_of(code: str) -> Stats:
    """HP, MP, AP and DP as the game stores them, before the screen's times a hundred."""
    built = scramble(read_digits(code))
    values: list[int] = []
    start = 0
    for size in GROUPS:
        values.append(int("".join(map(str, built[start : start + size]))) or 1)
        start += size
    hp, mp, ap, dp = values
    return hp, mp, ap, dp


def class_of(stats: Stats) -> int:
    """The class the game gives these numbers."""
    first = _below(stats, FIRST_THRESHOLDS)
    row = sum(1 for step in STEPS if first >= step)
    if row == SECOND_STEP and first < LOW_BITS:
        row = 0
    second = ((first << BITS) | _below(stats, ROWS[row])) & BYTE
    return CLASS_MAP[second]


def _below(stats: Stats, thresholds: tuple[int, ...]) -> int:
    """One bit per number under its threshold, HP first, then AP, MP and DP."""
    hp, mp, ap, dp = stats
    bits = 0
    for value, threshold in zip((hp, ap, mp, dp), thresholds, strict=True):
        bits = (bits << 1) | (1 if value < threshold else 0)
    return bits


def decode_battle_space(code: str) -> DatachCard:
    """A barcode as Battle Space reads it: its class, its four numbers, its magic and move."""
    code = validate_barcode(code)
    stats = stats_of(code)
    klass = class_of(stats)
    shown = tuple(
        GameStat(key, value * UNIT)
        for key, value in zip((HP_KEY, MP_KEY, AP_KEY, DP_KEY), stats, strict=True)
    )
    return DatachCard(
        code,
        Device.BATTLE_SPACE,
        GameKind.FIGHTER,
        klass,
        shown,
        (MAGIC_GROUPS[klass], SPECIALS[klass]),
    )


def build_battle_space(order: GameOrder, attempts: int = MAX_ATTEMPTS) -> DatachCard | None:
    """The strongest code the game reads as the class and numbers ordered, or None.

    Numbers are tried from the top, HP first, then AP, DP and MP, inside each
    combination of threshold bands that gives the class, up to a fixed number of
    attempts. When the numbers do not fit the class ordered, the class's
    strongest card stands in, and the caller sees it is not exact.
    """
    hp, ap, dp = order.stats
    card = _build((hp, Constraint.anything(), ap, dp), order.ident, attempts)
    if card is None:
        card = _nearest(order, attempts)
    if card is None and order.ident is not None:
        anything = Constraint.anything()
        return _build((anything, anything, anything, anything), order.ident, attempts)
    return card


def _nearest(order: GameOrder, attempts: int) -> DatachCard | None:
    """The card closest to exact numbers no code gives, stepping out a hundred at a time."""
    if not all(constraint.is_exact for constraint in order.stats):
        return None
    wanted = [constraint.minimum or 0 for constraint in order.stats]
    for step in range(1, MAX_STEPS + 1):
        for offsets in _shell(step):
            values = [
                max(UNIT, value + offset * UNIT)
                for value, offset in zip(wanted, offsets, strict=True)
            ]
            hp, ap, dp = (Constraint.exactly(value) for value in values)
            card = _build((hp, Constraint.anything(), ap, dp), order.ident, attempts)
            if card is not None:
                return card
    return None


def _shell(step: int) -> list[tuple[int, int, int]]:
    """The offsets exactly `step` away in at least one number, nearest in total first."""
    span = range(-step, step + 1)
    offsets = [
        (hp, ap, dp)
        for hp, ap, dp in product(span, span, span)
        if max(abs(hp), abs(ap), abs(dp)) == step
    ]
    return sorted(offsets, key=lambda offset: sum(map(abs, offset)))


def _build(
    constraints: tuple[Constraint, Constraint, Constraint, Constraint],
    ident: int | None,
    attempts: int,
) -> DatachCard | None:
    """The strongest code meeting the constraints and giving the class, or None."""
    budget = [attempts]
    for bands in _band_combinations(constraints, ident):
        code = _search(bands, constraints, budget)
        if code is not None:
            return decode_battle_space(code)
    return None


def strongest_battle_space() -> DatachCard:
    """The strongest fighter found: HP first, then AP, DP and MP, each as high as the rest allow.

    No code reads every number at its top: MP and AP at 999 fix digits four to
    nine, and HP at 9999 then needs a 1, a 7 and two 3s that no free digit can
    hold, so the numbers trade against each other in that order.
    """
    anything = Constraint.anything()
    card = build_battle_space(GameOrder(None, (anything, anything, anything)))
    return required(card, "no Battle Space code could be found")


def _band_combinations(
    constraints: tuple[Constraint, Constraint, Constraint, Constraint], ident: int | None
) -> Iterator[tuple[Band, Band, Band, Band]]:
    """Band combinations the order allows that give the class, strongest first."""
    hp, mp, ap, dp = (
        [band for band in _bands(index) if _allowed(band, constraint)]
        for index, constraint in enumerate(constraints)
    )
    for hp_band, ap_band, dp_band, mp_band in product(hp, ap, dp, mp):
        lows = (hp_band[0], mp_band[0], ap_band[0], dp_band[0])
        if ident is None or class_of(lows) == ident:
            yield hp_band, mp_band, ap_band, dp_band


def _bands(index: int) -> list[Band]:
    """The ranges one number falls in between the thresholds the class reads, highest first."""
    top = TOPS[index]
    cuts = sorted({row[_position(index)] for row in (FIRST_THRESHOLDS, *ROWS)} | {top + 1})
    bands = [(low, high - 1) for low, high in zip([1, *cuts], cuts, strict=False) if low < high]
    return bands[::-1]


def _allowed(band: Band, constraint: Constraint) -> bool:
    """Whether any value in the band meets the constraint."""
    return any(_values(band, constraint))


def _values(band: Band, constraint: Constraint) -> Iterator[int]:
    """The values in a band the constraint admits, highest first."""
    low, high = band
    return (value for value in range(high, low - 1, -1) if constraint.admits(value * UNIT))


def _search(
    bands: tuple[Band, Band, Band, Band],
    constraints: tuple[Constraint, Constraint, Constraint, Constraint],
    budget: list[int],
) -> str | None:
    """The first code in these bands, HP first, then AP, DP and MP, while attempts remain."""
    hp, mp, ap, dp = (
        list(_values(band, constraint)) for band, constraint in zip(bands, constraints, strict=True)
    )
    for hp_value, ap_value, dp_value, mp_value in product(hp, ap, dp, mp):
        budget[0] -= 1
        if budget[0] < 0:
            return None
        code = solve((hp_value, mp_value, ap_value, dp_value))
        if code is not None:
            return code
    return None


def _position(index: int) -> int:
    """Where the HP, MP, AP or DP number sits in the threshold rows, ordered HP, AP, MP, DP."""
    return (0, 2, 1, 3)[index]


def solve(stats: Stats) -> str | None:
    """A valid EAN-13 the game reads as exactly these numbers, or None."""
    for wanted in _digit_targets(stats):
        code = _solve_digits(wanted)
        if code is not None:
            return code
    return None


def _digit_targets(stats: Stats) -> Iterator[list[int]]:
    """The built digits these numbers can come from; a one may also be read from zeros."""
    options = [[value, 0] if value == 1 else [value] for value in stats]
    for picked in product(*options):
        text = "".join(f"{value:0{size}d}" for value, size in zip(picked, GROUPS, strict=True))
        yield [int(character) for character in text]


def _solve_digits(wanted: list[int]) -> str | None:
    """The code whose built digits are these, searching only the digits no rule fixes."""
    middle = [
        (wanted[4] - 1) % DIGITS,
        (wanted[7] - 1) % DIGITS,
        wanted[5],
        wanted[8],
        wanted[6],
        wanted[9],
    ]
    needs = [wanted[i] * INVERSE[weight] % DIGITS for i, weight in enumerate(HP_WEIGHTS)]
    heads = [_head_choices(middle, need) for need in needs]
    for head in product(*heads):
        tails = _tail_choices(list(head), needs)
        if tails is None:
            continue
        for d10, d11 in product(*tails):
            body = "".join(map(str, [*head, *middle, d10, d11]))
            code = body + str(expected_check_digit(body))
            if stats_digits(code) == wanted:
                return code
    return None


def _head_choices(middle: list[int], need: int) -> list[int]:
    """The values a head digit can take: those pointing at a fixed digit must find the need."""
    return [
        value
        for value in range(DIGITS)
        if not MIDDLE_FIRST <= value + SHIFT < MIDDLE_FIRST + len(middle)
        or middle[value + SHIFT - MIDDLE_FIRST] == need
    ]


def _tail_choices(head: list[int], needs: list[int]) -> tuple[list[int], list[int]] | None:
    """The values digits 10 and 11 may take once the head is chosen, or None when it fails."""
    forced: dict[int, int] = {}
    for digit, need in zip(head, needs, strict=True):
        position = digit + SHIFT
        if position < MIDDLE_FIRST and head[position] != need:
            return None
        if position >= TAIL_FIRST:
            if forced.get(position, need) != need:
                return None
            forced[position] = need
    return (
        [forced[TAIL_FIRST]] if TAIL_FIRST in forced else list(range(DIGITS)),
        [forced[TAIL_FIRST + 1]] if TAIL_FIRST + 1 in forced else list(range(DIGITS)),
    )


def stats_digits(code: str) -> list[int]:
    """The built digits of a code."""
    return scramble(read_digits(code))


def read_digits(code: str) -> list[int]:
    """The thirteen digits the game reads; it fills an EAN-8 out with its own first five."""
    return [int(character) for character in (code + code)[:EAN_13]]


def battle_space_entries() -> tuple[GameEntry, ...]:
    """Every class the game has, in its own order."""
    return tuple(
        GameEntry(number, GameKind.FIGHTER, CLASS_ENGLISH[number], CLASS_NAMES[number])
        for number in range(len(CLASS_NAMES))
    )


def battle_space_named(typed: str) -> int:
    """A class typed by number, English name or Japanese name."""
    text = typed.strip()
    if text.isdigit() and int(text) < len(CLASS_NAMES):
        return int(text)
    for number, names in enumerate(zip(CLASS_ENGLISH, CLASS_NAMES, strict=True)):
        if text.casefold() in (names[0].casefold(), names[1]):
            return number
    message = Said(
        f"no Battle Space class named {typed!r}",
        f"バトルスペースに {typed!r} という クラスは ない",
    )
    raise ValueError(message)


def battle_space_text(card: DatachCard) -> CardText:
    """A fighter's class, magic group, special move and spells, in both languages."""
    group, special = card.traits
    name = (CLASS_ENGLISH[card.ident], CLASS_NAMES[card.ident])
    if group not in MAGIC_LETTERS:
        move = NONE if special == NO_SPECIAL else (SPECIAL_ENGLISH[special], SPECIAL_NAMES[special])
        return CardText(name, NO_MAGIC, SPECIAL_HEADING, move)
    letter = MAGIC_LETTERS[group]
    detail = (f"Fighter, magic {letter}", f"せんし・まほう {letter}")
    spells = _spell_list(group)
    if special == NO_SPECIAL:
        return CardText(name, detail, SPELLS_HEADING, spells)
    return CardText(
        name,
        detail,
        BOTH_HEADING,
        (
            f"{SPECIAL_ENGLISH[special]}. Spells: {spells[0]}",
            f"{SPECIAL_NAMES[special]}。じゅもん: {spells[1]}",
        ),
    )


def _spell_list(group: int) -> Pair:
    """The spells a magic group casts, or a count when it casts every one."""
    if group == EVERY_SPELL_GROUP:
        return EVERY_SPELL
    return (
        ", ".join(SPELL_ENGLISH[spell] for spell in SPELLS[group]),
        "・".join(SPELL_NAMES[spell] for spell in SPELLS[group]),
    )
