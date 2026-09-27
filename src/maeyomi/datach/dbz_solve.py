"""Build a Datach Dragon Ball Z barcode to order, and prove it before returning it.

The game reads fields off a 40-bit stream that is a fixed scattering of ten
digits' bits, so the solver works backwards: it picks field values that give
the request, gathers them into a stream, and undoes the scattering. A stream is
only usable when each of the ten four-bit groups it yields is a decimal digit,
so several equivalent field values are tried: the character field repeats every
60, levels repeat in the level table, and many base and addend pairs give the
same stat. Every candidate is decoded by `decode_dbz` and compared with the
request before it is returned.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from functools import cache, partial
from typing import Final

from maeyomi.datach.dbz import (
    BONUS,
    STAT_FIELDS,
    STREAM_BITS,
    STREAM_BYTES,
    UNIT,
    DbzCard,
    DbzKind,
    decode_dbz,
)
from maeyomi.datach.dbz_names import ITEMS
from maeyomi.datach.dbz_tables import (
    ADDENDS,
    BASES,
    FIGHTER_SLOTS,
    FORMS,
    FORMS_BY_CHARACTER,
    ITEM_SLOTS,
    LEVELS,
    PERMUTATION,
)
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint

SEARCH_LIMIT: Final = 20_000
STREAM_LIMIT: Final = 400_000
ITEM_TAILS: Final = 4096
FIGHTER_KINDS: Final = (0, 1, 2)
ITEM_KIND: Final = 3
LEAD: Final = "00"
MAX_HP: Final = (max(BASES) + max(ADDENDS) + BONUS) * UNIT
MAX_HALVED: Final = MAX_HP // 2
NO_LEVEL: Final = 255
NO_MATCH: Final = "no barcode satisfies every constraint at once"
NEAR_WIDTHS: Final = (250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000)

type StatChoice = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class DbzRequest:
    """What a card should be. Stats are displayed values."""

    character: int | None = None
    kind: DbzKind = DbzKind.FIGHTER
    level: int | None = None
    no_level: bool = False
    hp: Constraint = field(default_factory=Constraint.anything)
    bp: Constraint = field(default_factory=Constraint.anything)
    dp: Constraint = field(default_factory=Constraint.anything)
    name: str = ""


@dataclass(frozen=True, slots=True)
class DbzSolveOutcome:
    """A verified card, or the reasons none exists."""

    request: DbzRequest
    card: DbzCard | None = None
    blockers: tuple[str, ...] = ()
    exact: bool = True


def solve_dbz(request: DbzRequest) -> DbzSolveOutcome:
    """Find a barcode the game reads as the request."""
    reasons = _blockers(request)
    if reasons:
        return DbzSolveOutcome(request, blockers=reasons)
    card = next(_found(request), None)
    if card is None:
        return DbzSolveOutcome(request, blockers=(NO_MATCH,))
    return DbzSolveOutcome(request, card=card)


def solve_dbz_nearest(request: DbzRequest) -> DbzSolveOutcome:
    """The exact card, or the one whose numbers sit closest to each exact value asked for.

    Every exact number is widened to a band around it, narrowest band first, and
    the first band holding any card gives the one closest to what was asked.
    """
    exact = solve_dbz(request)
    if exact.card is not None:
        return exact
    for width in NEAR_WIDTHS:
        widened = replace(
            request,
            hp=_around(request.hp, width),
            bp=_around(request.bp, width),
            dp=_around(request.dp, width),
        )
        near = min(_found(widened), key=partial(_distance, request), default=None)
        if near is not None:
            return DbzSolveOutcome(request, card=near, exact=False)
    return exact


def _distance(request: DbzRequest, card: DbzCard) -> int:
    """How far a card's numbers sit from the exact values asked for, summed."""
    pairs = ((request.hp, card.hp), (request.bp, card.bp), (request.dp, card.dp))
    return sum(
        abs(value - wanted.exact_value) for wanted, value in pairs if wanted.exact_value is not None
    )


def _around(constraint: Constraint, width: int) -> Constraint:
    """A band of the given half-width around an exact value, or the constraint unchanged."""
    if constraint.exact_value is None:
        return constraint
    return Constraint.between(
        max(0, constraint.exact_value - width), constraint.exact_value + width
    )


def request_from(shared: CardRequest, *, character: int | None, level: int | None) -> DbzRequest:
    """The game's request from the shared one: attack is BP and defence is DP."""
    return DbzRequest(
        character=character,
        kind=DbzKind.ITEM if character in ITEMS else DbzKind.FIGHTER,
        level=level,
        hp=shared.hp,
        bp=shared.st,
        dp=shared.df,
        name=shared.name,
    )


def unread_fields(shared: CardRequest, *, back_read: bool) -> tuple[str, ...]:
    """Every field of the shared request the game has no place for, in a fixed order."""
    anything = Constraint.anything()
    present = {
        "race": shared.race is not None,
        "class": shared.character_class is not None,
        "job": shared.job is not None,
        "speed": shared.speed is not None,
        "ability": shared.special is not None,
        "herbs": shared.pp != anything,
        "magic": shared.mp != anything,
        "back-read": back_read,
    }
    return tuple(name for name, given in present.items() if given)


def _found(request: DbzRequest) -> Iterator[DbzCard]:
    """Every card the search reaches that the game reads as the request, in search order."""
    streams = itertools.islice(_streams(request), STREAM_LIMIT)
    codes = (_barcode(digits) for digits in map(digits_for, streams) if digits)
    decoded = map(decode_dbz, itertools.islice(codes, SEARCH_LIMIT))
    return (card for card in decoded if _matches(request, card))


def digits_for(stream: int) -> tuple[int, ...] | None:
    """The ten digits that scatter into this stream, or None if one would pass 9."""
    spread = _spread_of(stream)
    if not _decimal(spread):
        return None
    return tuple(spread >> (4 * index) & 0x0F for index in range(10))


def _stream_bit(entry: int) -> int:
    """The bit of the 40-bit stream integer a permutation entry names."""
    return (STREAM_BYTES - 1 - (entry >> 4)) * 8 + (entry & 0x0F)


_DIGIT_BIT: Final = {_stream_bit(entry): index for index, entry in enumerate(PERMUTATION)}
_HIGH_BITS: Final = sum(1 << (4 * index + 3) for index in range(10))


def _spread_of(stream: int) -> int:
    """The stream's bits laid back out as ten four-bit digits, digit 0 lowest."""
    return sum(1 << _DIGIT_BIT[bit] for bit in range(STREAM_BITS) if stream >> bit & 1)


_spread: Final = cache(_spread_of)
"""`_spread_of` remembered, for the strongest-card search that asks for the same parts often."""


def _decimal(spread: int) -> bool:
    """Whether every four-bit digit is at most 9: none sets bit 3 with bit 2 or bit 1."""
    return not (spread & (spread << 1 | spread << 2) & _HIGH_BITS)


def _barcode(digits: tuple[int, ...]) -> str:
    """An EAN-13 carrying the ten digits after two free ones."""
    body = LEAD + "".join(map(str, digits))
    return body + str(expected_check_digit(body))


def _matches(request: DbzRequest, card: DbzCard) -> bool:
    """Whether a decoded card is what was asked for."""
    wrong_character = request.character not in {None, card.character}
    if card.kind is not request.kind or wrong_character:
        return False
    if request.kind is DbzKind.ITEM:
        return True
    level_ok = (card.level is None) if request.no_level else request.level in {None, card.level}
    stats = (request.hp.admits(card.hp), request.bp.admits(card.bp), request.dp.admits(card.dp))
    return level_ok and all(stats)


def _blockers(request: DbzRequest) -> tuple[str, ...]:
    """Every reason the request cannot be met, decided without searching."""
    reasons: list[str] = []
    known = _item_ids() if request.kind is DbzKind.ITEM else _fighter_ids()
    if request.character is not None and request.character not in known:
        reasons.append(f"character {request.character} is not one the game can produce")
    if request.level is not None and request.level not in _levels():
        reasons.append(f"level {request.level} is not one the game can produce")
    for name, ceiling in (("hp", MAX_HP), ("bp", MAX_HALVED), ("dp", MAX_HALVED)):
        reasons += _stat_blockers(name, getattr(request, name), ceiling)
    return tuple(reasons)


def _stat_blockers(name: str, constraint: Constraint, ceiling: int) -> list[str]:
    """Reasons one displayed stat cannot be met."""
    reasons: list[str] = []
    if constraint.exact_value is not None and constraint.exact_value % UNIT:
        reasons.append(f"{name} of {constraint.exact_value} is not a multiple of {UNIT}")
    if constraint.minimum is not None and constraint.minimum > ceiling:
        reasons.append(f"{name} of {constraint.minimum} is above {ceiling}")
    return reasons


def _fighter_ids() -> frozenset[int]:
    """Every character id and every form the game can produce."""
    return frozenset(identifier for identifier, _ in FIGHTER_SLOTS) | {form for *_, form in FORMS}


def _item_ids() -> frozenset[int]:
    """Every item id the game can produce."""
    return frozenset(identifier for identifier, _ in ITEM_SLOTS)


def _levels() -> frozenset[int]:
    """Every level the game shows."""
    return frozenset(level for level in LEVELS if level != NO_LEVEL)


def _streams(request: DbzRequest) -> Iterator[int]:
    """Candidate streams, items and fighters alike."""
    if request.kind is DbzKind.ITEM:
        return _item_streams(request)
    return _fighter_streams(request)


def _item_streams(request: DbzRequest) -> Iterator[int]:
    """Kind 3, a character field for the item, and a free tail the game never reads."""
    values = _field_values(ITEM_SLOTS, request.character)
    return (
        ITEM_KIND << 38 | value << 30 | tail
        for value, tail in itertools.product(values, range(ITEM_TAILS))
    )


def _fighter_streams(request: DbzRequest) -> Iterator[int]:
    """Every combination of kind, character, level and stats worth decoding."""
    heads = itertools.product(
        FIGHTER_KINDS, _fighter_field_values(request.character), _level_indices(request)
    )
    choices = (
        _choices(request.hp, halved=False),
        _choices(request.bp, halved=True),
        _choices(request.dp, halved=True),
    )
    return (
        _assemble(kind, value, level, stats)
        for kind, value, level in heads
        for stats in itertools.product(*choices)
    )


def _assemble(kind: int, value: int, level: int, stats: tuple[StatChoice, ...]) -> int:
    """Gather the fields into a stream, top bit first."""
    stream = kind << 38 | value << 30 | level << 27
    for index, (base, addend, bonus) in enumerate(stats):
        stream |= (base << 5 | addend << 1 | bonus) << (18 - 9 * index)
    return stream


def _field_values(table: tuple[tuple[int, int], ...], identifier: int | None) -> list[int]:
    """Every 8-bit character field whose slot is the id, or every field for any id."""
    ends = list(itertools.accumulate(count for _, count in table))
    ids = [identifier for identifier, _ in table]
    return [
        value
        for value in range(256)
        if identifier is None
        or ids[next(index for index, end in enumerate(ends) if value % 60 + 1 <= end)] == identifier
    ]


def _fighter_field_values(character: int | None) -> list[int]:
    """Character fields for the character itself, or for the base it transforms from."""
    bases = [character] if character in {identifier for identifier, _ in FIGHTER_SLOTS} else []
    bases += [
        base
        for base, records in FORMS_BY_CHARACTER.items()
        if any(FORMS[record][3] == character for record in records)
    ]
    if character is None:
        return _field_values(FIGHTER_SLOTS, None)
    return [value for base in bases for value in _field_values(FIGHTER_SLOTS, base)]


def _level_indices(request: DbzRequest) -> list[int]:
    """Indices into the level table that give the requested level."""
    if request.no_level:
        return [index for index, level in enumerate(LEVELS) if level == NO_LEVEL]
    return [
        index
        for index, level in enumerate(LEVELS)
        if (request.level is None and level != NO_LEVEL) or level == request.level
    ]


def _choices(constraint: Constraint, *, halved: bool) -> list[StatChoice]:
    """Every choice the constraint admits: nearest the middle of a band, else strongest first."""
    ranked = _ranked(constraint, halved=halved)
    if constraint.minimum is None or constraint.maximum is None:
        return [choice for _, choice in ranked]
    middle = (constraint.minimum + constraint.maximum) // 2
    return [choice for _, choice in sorted(ranked, key=lambda pair: abs(pair[0] - middle))]


def _ranked(constraint: Constraint, *, halved: bool) -> list[tuple[int, StatChoice]]:
    """Admitted choices with the value each displays, strongest first."""
    widths = STAT_FIELDS
    options = itertools.product(range(1 << widths[0]), range(1 << widths[1]), (0, 1))
    shown = [
        (_shown(base, addend, bonus, halved=halved), (base, addend, bonus))
        for base, addend, bonus in options
    ]
    admitted = [(value, choice) for value, choice in shown if constraint.admits(value)]
    return sorted(admitted, key=lambda pair: -pair[0])


def _shown(base: int, addend: int, bonus: int, *, halved: bool) -> int:
    """The displayed value a choice produces."""
    units = BASES[base] + ADDENDS[addend] + (BONUS if bonus == 0 else 0)
    return (units // 2 if halved else units) * UNIT


type Ranked = list[tuple[int, StatChoice]]


@dataclass(frozen=True, slots=True)
class _Search:
    """The fixed parts of one strongest-card search."""

    request: DbzRequest
    head: tuple[int, int, int]
    ranked: tuple[Ranked, Ranked, Ranked]


def strongest_dbz(request: DbzRequest) -> DbzCard | None:
    """The printable fighter meeting the request with the highest HP, BP and DP together."""
    if _blockers(request):
        return None
    ranked = (
        _ranked(request.hp, halved=False),
        _ranked(request.bp, halved=True),
        _ranked(request.dp, halved=True),
    )
    heads = itertools.product(
        FIGHTER_KINDS, _fighter_field_values(request.character), _level_indices(request)
    )
    best: tuple[int, DbzCard | None] = (-1, None)
    for head in heads:
        best = _best_for_head(_Search(request, head, ranked), best)
    return best[1]


def _best_for_head(search: _Search, best: tuple[int, DbzCard | None]) -> tuple[int, DbzCard | None]:
    """Improve on the best total with this kind, character field and level."""
    hp_ranked, bp_ranked, dp_ranked = search.ranked
    ceiling = bp_ranked[0][0] + dp_ranked[0][0] if bp_ranked and dp_ranked else 0
    for hp_value, hp_choice in hp_ranked:
        if hp_value + ceiling <= best[0]:
            break
        for bp_value, bp_choice in bp_ranked:
            if hp_value + bp_value + dp_ranked[0][0] <= best[0]:
                break
            best = _best_dp(search, (hp_value + bp_value, hp_choice, bp_choice), best)
    return best


def _best_dp(
    search: _Search, partial: tuple[int, StatChoice, StatChoice], best: tuple[int, DbzCard | None]
) -> tuple[int, DbzCard | None]:
    """The strongest DP choice that completes a printable card beating the best total."""
    subtotal, hp_choice, bp_choice = partial
    kind, value, level = search.head
    fixed = _spread(_assemble(kind, value, level, (hp_choice, bp_choice, (0, 0, 0))))
    for dp_value, dp_choice in search.ranked[2]:
        total = subtotal + dp_value
        if total <= best[0]:
            return best
        spread = fixed | _spread(_assemble(0, 0, 0, ((0, 0, 0), (0, 0, 0), dp_choice)))
        if not _decimal(spread):
            continue
        card = decode_dbz(_barcode(tuple(spread >> (4 * index) & 0x0F for index in range(10))))
        if _matches(search.request, card):
            return total, card
    return best
