"""The Datach games after Dragon Ball Z, each described the same way.

Every surface that serves a game, the registry, the command line, the web page
and the card faces, looks the game up here rather than branching on it, so a
game added to this table is a game every surface supports.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GamePick
from maeyomi.datach.jleague import build_jleague, decode_jleague
from maeyomi.datach.jleague_names import PLAYERS as JLEAGUE_PLAYERS
from maeyomi.datach.jleague_names import TEAM_SLOTS, TEAMS, ident_of, names_of
from maeyomi.datach.jleague_names import card_named as jleague_named
from maeyomi.datach.sdgundam import (
    SdGundamOrder,
    build_sdgundam,
    command_names,
    decode_sdgundam,
    picks_for,
    strongest_sdgundam,
)
from maeyomi.datach.sdgundam_names import COMMANDS, UNITS, WEAPONS, card_named, command_number
from maeyomi.datach.sdgundam_tables import FIRST_COMMAND
from maeyomi.datach.ultraman import UltramanOrder, build_ultraman, decode_ultraman
from maeyomi.datach.ultraman import strongest_ultraman as _strongest_ultraman
from maeyomi.datach.ultraman_names import NAMES as ULTRAMAN_NAMES
from maeyomi.datach.ultraman_names import type_named
from maeyomi.datach.ultraman_tables import FIRST_ITEM
from maeyomi.datach.yuyu import YuYuOrder, build_yuyu, decode_yuyu, strongest_yuyu
from maeyomi.datach.yuyu import picks_for as yuyu_picks
from maeyomi.datach.yuyu_names import CHARACTERS as YUYU_CHARACTERS
from maeyomi.datach.yuyu_names import ITEMS as YUYU_ITEMS
from maeyomi.datach.yuyu_names import TECHNIQUE_NAMES, bonus_text
from maeyomi.datach.yuyu_names import card_named as yuyu_named
from maeyomi.datach.yuyu_tables import SECRET_CHARACTER
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

type Pair = tuple[str, str]

FIGHTER: Final[Pair] = ("Fighter", "せんし")
ITEM: Final[Pair] = ("Item card", "アイテム カード")
TYPE: Final[Pair] = ("Type", "タイプ")
WEAPONS_HEADING: Final[Pair] = ("Weapons", "ぶき")
EFFECT: Final[Pair] = ("Effect", "こうか")
COMMAND_CARD: Final[Pair] = ("Command card", "コマンド カード")
TECHNIQUES_HEADING: Final[Pair] = ("Techniques", "わざ")
HIDDEN: Final[Pair] = ("Hidden fighter", "かくし キャラクター")
NO_TECHNIQUE: Final[Pair] = ("No technique", "わざ なし")
TEAM_CARD: Final[Pair] = ("Team card", "チーム カード")
PLAYER_HEADING: Final[Pair] = ("Player", "せんしゅ")
TEAM_HEADING: Final[Pair] = ("Team", "チーム")


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
    """Everything a surface needs to read, build, list and describe one game's cards."""

    decode: Callable[[str], DatachCard]
    build: Callable[[GameOrder], DatachCard | None]
    strongest: Callable[[], DatachCard] | None
    entries: Callable[[], tuple[GameEntry, ...]]
    describe: Callable[[DatachCard], CardText]
    named: Callable[[str], int]
    stat_keys: tuple[str, ...]
    picks: Callable[[int], tuple[GamePick, ...]] = lambda _: ()


def _ultraman_order(order: GameOrder) -> DatachCard | None:
    """Build an Ultraman Club card: its three numbers are PW, ST and SP."""
    return build_ultraman(UltramanOrder(order.ident, *order.stats))


def _ultraman_entries() -> tuple[GameEntry, ...]:
    """Every type Ultraman Club reads, fighters first."""
    return tuple(
        GameEntry(ident, GameKind.ITEM if ident >= FIRST_ITEM else GameKind.FIGHTER, *names)
        for ident, names in ULTRAMAN_NAMES.items()
    )


def _ultraman_text(card: DatachCard) -> CardText:
    """An Ultraman Club card's name, whether it is a fighter or an item, and its type."""
    return CardText(
        name=ULTRAMAN_NAMES[card.ident],
        detail=ITEM if card.kind is GameKind.ITEM else FIGHTER,
        heading=TYPE,
        power=(f"No. {card.ident} in the game's list", f"ゲームの いちらんの {card.ident}ばん"),
    )


def _sdgundam_order(order: GameOrder) -> DatachCard | None:
    """Build an SD Gundam Wars card: its three numbers are HP, AP and DP."""
    return build_sdgundam(SdGundamOrder(order.ident, order.stats, order.picks))


def _sdgundam_entries() -> tuple[GameEntry, ...]:
    """Every unit, then every command card, SD Gundam Wars reads."""
    units = tuple(
        GameEntry(ident, GameKind.UNIT, unit.english, unit.japanese)
        for ident, unit in UNITS.items()
    )
    commands = tuple(
        GameEntry(
            number + FIRST_COMMAND - 1, GameKind.COMMAND, *command_names(number + FIRST_COMMAND - 1)
        )
        for number in COMMANDS
    )
    return units + commands


def _sdgundam_text(card: DatachCard) -> CardText:
    """A unit's model number and weapons, or a command's effect and cost."""
    if card.kind is GameKind.COMMAND:
        command = COMMANDS[command_number(card.ident)]
        return CardText(
            name=(command.english, command.japanese),
            detail=COMMAND_CARD,
            heading=EFFECT,
            power=(
                f"{command.effect} Costs {command.cost} CP.",
                f"{command.effect_japanese}。しょうひ CP {command.cost}",
            ),
        )
    unit = UNITS[card.ident]
    short, long, _ = card.traits
    return CardText(
        name=(unit.english, unit.japanese),
        detail=(unit.model, unit.model),
        heading=WEAPONS_HEADING,
        power=(
            f"SR {WEAPONS[short][0]}, LR {WEAPONS[long][0]}",
            f"SR {WEAPONS[short][1]}  LR {WEAPONS[long][1]}",
        ),
    )


def _yuyu_order(order: GameOrder) -> DatachCard | None:
    """Build a Yu Yu Hakusho card: its numbers are fixed, so only its choices count."""
    return build_yuyu(YuYuOrder(order.ident, order.picks))


def _yuyu_entries() -> tuple[GameEntry, ...]:
    """Every character, the hidden one last, then every item Yu Yu Hakusho reads."""
    fighters = tuple(
        GameEntry(ident, GameKind.FIGHTER, *names)
        for ident, names in YUYU_CHARACTERS.items()
        if ident != SECRET_CHARACTER
    )
    hidden = GameEntry(SECRET_CHARACTER, GameKind.HIDDEN, *YUYU_CHARACTERS[SECRET_CHARACTER])
    items = tuple(
        GameEntry(ident, GameKind.ITEM, item.english, item.japanese)
        for ident, item in YUYU_ITEMS.items()
    )
    return (*fighters, hidden, *items)


def _yuyu_text(card: DatachCard) -> CardText:
    """A character's techniques, or what an item does."""
    if card.kind is GameKind.ITEM:
        item = YUYU_ITEMS[card.ident]
        effect = (
            bonus_text(card.value("YHP"), card.value("YSP"))
            if card.stats
            else (item.effect, item.effect_japanese)
        )
        return CardText((item.english, item.japanese), ITEM, EFFECT, effect)
    names = [TECHNIQUE_NAMES[technique] for technique in card.traits[1:]]
    power = (
        (", ".join(name for name, _ in names), "・".join(name for _, name in names))
        if names
        else NO_TECHNIQUE
    )
    detail = HIDDEN if card.kind is GameKind.HIDDEN else FIGHTER
    return CardText(YUYU_CHARACTERS[card.ident], detail, TECHNIQUES_HEADING, power)


def _jleague_order(order: GameOrder) -> DatachCard | None:
    """Build a J.League card: it names a team or a player and carries nothing else."""
    return build_jleague(order.ident)


def _jleague_entries() -> tuple[GameEntry, ...]:
    """Each team's own card, then its fifteen players, team by team."""
    return tuple(
        entry
        for team, names in TEAMS.items()
        for entry in (
            GameEntry(ident_of(team, 0), GameKind.TEAM, *names),
            *(
                GameEntry(ident_of(team, number), GameKind.PLAYER, *JLEAGUE_PLAYERS[team, number])
                for number in range(1, TEAM_SLOTS)
            ),
        )
    )


def _jleague_text(card: DatachCard) -> CardText:
    """A player's team and slot, or a team card's club."""
    team, number = divmod(card.ident, TEAM_SLOTS)
    club = TEAMS[team]
    if card.kind is GameKind.TEAM:
        return CardText(club, TEAM_CARD, TEAM_HEADING, club)
    return CardText(
        names_of(card.ident),
        club,
        PLAYER_HEADING,
        (f"No. {number} of {club[0]}", f"{club[1]} の {number}ばん"),
    )


GAMES: Final[dict[Device, DatachGame]] = {
    Device.DATACH_ULTRAMAN: DatachGame(
        decode=decode_ultraman,
        build=_ultraman_order,
        strongest=_strongest_ultraman,
        entries=_ultraman_entries,
        describe=_ultraman_text,
        named=type_named,
        stat_keys=("PW", "UST", "USP"),
    ),
    Device.DATACH_SD_GUNDAM: DatachGame(
        decode=decode_sdgundam,
        build=_sdgundam_order,
        strongest=strongest_sdgundam,
        entries=_sdgundam_entries,
        describe=_sdgundam_text,
        named=card_named,
        stat_keys=("GHP", "AP", "GDP"),
        picks=picks_for,
    ),
    Device.DATACH_YUYU: DatachGame(
        decode=decode_yuyu,
        build=_yuyu_order,
        strongest=strongest_yuyu,
        entries=_yuyu_entries,
        describe=_yuyu_text,
        named=yuyu_named,
        stat_keys=("YHP", "YSP"),
        picks=yuyu_picks,
    ),
    Device.DATACH_JLEAGUE: DatachGame(
        decode=decode_jleague,
        build=_jleague_order,
        strongest=None,
        entries=_jleague_entries,
        describe=_jleague_text,
        named=jleague_named,
        stat_keys=(),
    ),
}


def game_for(device: Device) -> DatachGame | None:
    """The game a device is, or None for a machine and for Dragon Ball Z."""
    return GAMES.get(device)
