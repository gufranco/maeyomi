"""The shapes every game served through the dispatch table shares.

A surface asks a game for its cards through a `DatachGame`, orders one with a
`GameOrder`, lists them as `GameEntry` rows and prints each with its
`CardText`, so these live apart from the table that fills them in.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GamePick
from maeyomi.models.constraint import Constraint

type Pair = tuple[str, str]

FIGHTING_KINDS: Final = frozenset(
    {GameKind.FIGHTER, GameKind.UNIT, GameKind.PLAYER, GameKind.HIDDEN, GameKind.EFFECT}
)
"""The kinds a random sheet draws, unless a game names its own."""


@dataclass(frozen=True, slots=True)
class GameOrder:
    """A card asked of a game: which one, what its numbers must be, and its other choices."""

    ident: int | None
    stats: tuple[Constraint, Constraint, Constraint]
    picks: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True, slots=True)
class GameEntry:
    """One card a game can read, as its list of cards names it."""

    ident: int
    kind: GameKind
    english: str
    japanese: str


@dataclass(frozen=True, slots=True)
class CardText:
    """What a card says in both languages: its name, what it is, and one more line."""

    name: Pair
    detail: Pair
    heading: Pair
    power: Pair


@dataclass(frozen=True, slots=True)
class DatachGame:
    """Everything a surface needs to read, build, list and describe one game's cards.

    `companion` is the second card an order prints beside the first, for a game
    that reads a pair of cards, and `strongest_companion` is the strongest
    card's partner.
    """

    decode: Callable[[str], DatachCard]
    build: Callable[[GameOrder], DatachCard | None]
    strongest: Callable[[], DatachCard] | None
    entries: Callable[[], tuple[GameEntry, ...]]
    describe: Callable[[DatachCard], CardText]
    named: Callable[[str], int]
    stat_keys: tuple[str, ...]
    picks: Callable[[int], tuple[GamePick, ...]] = lambda _: ()
    datach_reader: bool = True
    drawable: frozenset[GameKind] = FIGHTING_KINDS
    companion: Callable[[GameOrder], DatachCard | None] = lambda _: None
    strongest_companion: Callable[[], DatachCard | None] = lambda: None
