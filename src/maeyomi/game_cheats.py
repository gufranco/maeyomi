"""The cheat kinds each game offers, built from the game's own builders.

A game offers its strongest card first. A game that can be strongest in more
than one way, or that reads more than one kind of card, offers each way after
it: a card at the top of one number, or every item at its top. A kind that
would print the strongest card again is left out.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from functools import cache
from itertools import product
from typing import Final

from maeyomi.datach.battlerush import STRONGEST, RobotOrder, build_robot, robot_numbers
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.datach.games import GAMES
from maeyomi.datach.sdgundam import strongest_sdgundam
from maeyomi.datach.sdgundam_names import UNITS
from maeyomi.datach.ultraman import strongest_ultraman
from maeyomi.gameboy.famista3 import BATTER, PICK_KEY, PITCHER, famista3_text
from maeyomi.gameboy.famjock2 import MARE, STALLION, strongest_boxed
from maeyomi.gameboy.kattobi import code_for, decode_kattobi, reading_of
from maeyomi.gameboy.monstermaker import LATER_KEY, stats_of
from maeyomi.games.barcode_world import HUNDRED
from maeyomi.games.barcode_world import TOP_HP as C0_TOP_HP
from maeyomi.games.barcode_world import TOP_STAT as C0_TOP_STAT
from maeyomi.games.excite94 import FIRST_TEAM, KEEPER_SLOTS, build_excite94_player, player_ident
from maeyomi.games.excite94_players import PLAYERS
from maeyomi.games.hatayama import TOP_STAMINA
from maeyomi.games.hatayama import TOP_STAT as HATAYAMA_TOP_STAT
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

ANY: Final = Constraint.anything()
ANYTHING: Final = (ANY, ANY, ANY)
TEAMS: Final = 12
PARTS: Final = 32
PILOTS: Final = 16
TOP_LEVELS: Final = (7, 7, 7, 7)
KEPT: Final = 5
TENS: Final = 10
GRADE_BASE: Final = 16
LATER_MP: Final = 2
LATER_AP: Final = 3
EFFECT_GAMES: Final = (
    Device.LUPIN,
    Device.DONALD,
    Device.SPIDERMAN,
    Device.ALICE,
    Device.DORAEMON2,
    Device.DORAEMON3,
    Device.YOUSEI,
    Device.DSLAYER2,
)


@dataclass(frozen=True, slots=True)
class GameCheat:
    """One way a game's cards are at their strongest, the number it tops, and its cards."""

    key: str
    english: str
    japanese: str
    cards: Callable[[], tuple[DatachCard, ...]]
    stat: str | None = None


STRONGEST_KEY: Final = "strongest"
STRONGEST_ENGLISH: Final = "Strongest card"
STRONGEST_JAPANESE: Final = "いちばん つよい カード"


def game_cheats(device: Device) -> tuple[GameCheat, ...]:
    """Every cheat kind the game offers, the strongest card first."""
    game = GAMES.get(device)
    first = () if game is None or game.strongest is None else (_strongest_cheat(device),)
    more = KINDS.get(device)
    return (*first, *(() if more is None else more()))


def _strongest_cheat(device: Device) -> GameCheat:
    """The game's strongest card, and its partner for a game that reads pairs."""
    game = GAMES[device]

    def cards() -> tuple[DatachCard, ...]:
        assert game.strongest is not None
        partner = game.strongest_companion()
        first = game.strongest()
        return (first,) if partner is None else (first, partner)

    return GameCheat(STRONGEST_KEY, STRONGEST_ENGLISH, STRONGEST_JAPANESE, cards)


def value_of(card: DatachCard, key: str) -> int:
    """One of a card's numbers, 0 when the card does not carry it."""
    return max((stat.value for stat in card.stats if stat.key == key), default=0)


def _total(card: DatachCard) -> int:
    """Every number a card carries, added together."""
    return sum(stat.value for stat in card.stats)


def _best_by(stat: str, cards: Iterable[DatachCard | None]) -> DatachCard:
    """The card with the most of one number, then the most of all of them."""
    return max(
        (card for card in cards if card is not None),
        key=lambda card: (value_of(card, stat), _total(card)),
    )


def _build(
    device: Device, ident: int, picks: tuple[tuple[str, int], ...] = ()
) -> DatachCard | None:
    """A card the game's own builder makes for this entry and these choices."""
    return GAMES[device].build(GameOrder(ident, ANYTHING, picks))


def _top_pick(device: Device, ident: int, key: str) -> tuple[tuple[str, int], ...]:
    """The highest value a choice offers an entry, or nothing when it offers no such choice."""
    pick = next((pick for pick in GAMES[device].picks(ident) if pick.key == key), None)
    return () if pick is None else ((key, max(option.value for option in pick.options)),)


def _entries(device: Device, kind: GameKind) -> list[int]:
    """Every entry of one kind in the game's own list."""
    return [entry.ident for entry in GAMES[device].entries() if entry.kind is kind]


def _numbered(device: Device, stat: str, english: str, japanese: str) -> GameCheat:
    """A kind topping one number over every card `_candidates` offers for the game."""
    key = english.rsplit(maxsplit=1)[-1].lower()
    return GameCheat(key, english, japanese, lambda: (_best_by(stat, _candidates(device)),), stat)


@cache
def _candidates(device: Device) -> tuple[DatachCard, ...]:
    """Every card a numbered kind chooses from, built once per game."""
    return tuple(card for card in CANDIDATES[device]() if card is not None)


def _monster_maker_cards() -> Iterable[DatachCard | None]:
    """Every hero with every character and level it can give later."""
    device = Device.MONSTER_MAKER
    for hero in _entries(device, GameKind.FIGHTER):
        pick = GAMES[device].picks(hero)[0]
        yield from (_build(device, hero, ((LATER_KEY, option.value),)) for option in pick.options)


def later_numbers(card: DatachCard) -> tuple[int, ...]:
    """The move, DP, MP, AP and HP of what a Monster Maker card gives later in the game."""
    _, later, level = card.traits
    return stats_of(later, level or 1)


def _later_best(place: int) -> DatachCard:
    """The Monster Maker card giving the most of one number later, then the most of all."""
    return max(
        _candidates(Device.MONSTER_MAKER),
        key=lambda card: (later_numbers(card)[place], sum(later_numbers(card)[1:])),
    )


def _battle_space_cards() -> Iterable[DatachCard | None]:
    """Every class at the most its numbers allow."""
    return (
        _build(Device.BATTLE_SPACE, ident)
        for ident in _entries(Device.BATTLE_SPACE, GameKind.FIGHTER)
    )


def _sdgundam_cards() -> Iterable[DatachCard | None]:
    """Every mobile suit at every top bonus."""
    return (strongest_sdgundam(unit) for unit in UNITS)


def _bardigun_cards() -> Iterable[DatachCard | None]:
    """Every creature a Bardigun barcode can be sure to hatch."""
    device = Device.BARDIGUN
    return (_build(device, species) for species in _entries(device, GameKind.FIGHTER))


CANDIDATES: Final[dict[Device, Callable[[], Iterable[DatachCard | None]]]] = {
    Device.MONSTER_MAKER: _monster_maker_cards,
    Device.BATTLE_SPACE: _battle_space_cards,
    Device.DATACH_SD_GUNDAM: _sdgundam_cards,
    Device.BARDIGUN: _bardigun_cards,
}


def _items(device: Device, key: str | None, english: str, japanese: str) -> GameCheat:
    """Every item the game reads, each at the top of its choice when it has one."""

    def cards() -> tuple[DatachCard, ...]:
        built = (
            _build(device, ident, () if key is None else _top_pick(device, ident, key))
            for ident in _entries(device, GameKind.ITEM)
        )
        return tuple(card for card in built if card is not None)

    return GameCheat("items", english, japanese, cards)


def _ultraman_items() -> tuple[DatachCard, ...]:
    """Every item type with PW, ST and SP at the top."""
    return tuple(
        strongest_ultraman(ident) for ident in _entries(Device.DATACH_ULTRAMAN, GameKind.ITEM)
    )


def _warrior(
    device: Device, stats: tuple[Constraint, Constraint, Constraint], *, job: bool
) -> GameCheat:
    """The warrior at the top of every number, the highest warrior job when it has one."""

    def cards() -> tuple[DatachCard, ...]:
        picks = _top_pick(device, 0, "job") if job else ()
        card = GAMES[device].build(GameOrder(0, stats, picks))
        return () if card is None else (card,)

    return GameCheat("warrior", "Warrior", "せんし", cards)


def _effects(device: Device) -> tuple[GameCheat, ...]:
    """Every effect but the strongest, one kind each."""
    game = GAMES[device]
    assert game.strongest is not None
    first = game.strongest().ident
    return tuple(
        GameCheat(
            f"effect-{entry.ident}",
            entry.english,
            entry.japanese,
            lambda ident=entry.ident: _one(device, ident),
        )
        for entry in game.entries()
        if entry.ident != first
    )


def _one(device: Device, ident: int) -> tuple[DatachCard, ...]:
    """One entry's card, or none when the game cannot print it."""
    card = _build(device, ident)
    return () if card is None else (card,)


def _keeper() -> tuple[DatachCard, ...]:
    """The hidden keeper graded highest at defending, then at everything."""
    keepers = [
        player_ident(team, slot)
        for team in range(FIRST_TEAM, FIRST_TEAM + TEAMS)
        for slot in KEEPER_SLOTS
    ]
    ranked = sorted(keepers, key=lambda ident: _grades(PLAYERS[ident][1]))
    card = next(card for card in map(build_excite94_player, ranked) if card is not None)
    return (card,)


def _grades(grades: str) -> tuple[int, int]:
    """A keeper's defending grade, then every grade together, A lowest."""
    nibbles = [int(nibble, GRADE_BASE) for nibble in grades]
    return nibbles[2], sum(nibbles)


def _robot(stat: str) -> tuple[DatachCard, ...]:
    """The robot with the most of one number, its parts found by trying each that feeds it."""
    feeding = {"attack": "shoulder", "defense": "body", "speed": "foot"}[stat]
    orders = (
        replace(STRONGEST, head=head, pilot=pilot, levels=TOP_LEVELS, **{feeding: part})
        for head, part, pilot in product(range(PARTS), range(PARTS), range(PILOTS))
    )
    ranked = sorted(orders, key=lambda order: _robot_rank(order, stat), reverse=True)
    return next(pair for pair in map(build_robot, ranked) if pair is not None)


def _robot_rank(order: RobotOrder, stat: str) -> tuple[int, int]:
    """How a robot ranks for one number: that number, then attack, defense and speed together."""
    numbers = robot_numbers(order)
    return numbers[stat], numbers["attack"] + numbers["defense"] + numbers["speed"]


@cache
def _torque() -> tuple[DatachCard, ...]:
    """The car and code giving the most torque, then the most power."""
    kept = max(
        ((e0, e1, e2, e3, e4) for e0, e1, e2, e3, e4 in product(range(TENS), repeat=KEPT)),
        key=lambda digits: (reading_of(digits).torque, reading_of(digits).power),
    )
    return (decode_kattobi(code_for(kept)),)


def _famista(kind: int, rank: Callable[[DatachCard], float]) -> tuple[DatachCard, ...]:
    """The rookie of one kind ranked highest, over every player a code reaches."""
    pick = GAMES[Device.FAMISTA3].picks(kind)[0]
    cards = (_build(Device.FAMISTA3, kind, ((PICK_KEY, option.value),)) for option in pick.options)
    return (max((card for card in cards if card is not None), key=rank),)


def _average(card: DatachCard) -> float:
    """A batter's average, from the line its card prints."""
    return float(famista3_text(card).power[0])


def _earned_runs(card: DatachCard) -> float:
    """A pitcher's ERA turned so that lower ranks higher."""
    return -float(famista3_text(card).power[0])


def _c0_tops() -> tuple[Constraint, Constraint, Constraint]:
    """Barcode World's and Senki's HP, ST and DF at the most they read."""
    return (
        Constraint.exactly(C0_TOP_HP * HUNDRED),
        Constraint.exactly(C0_TOP_STAT * HUNDRED),
        Constraint.exactly(C0_TOP_STAT * HUNDRED),
    )


def _hatayama_tops() -> tuple[Constraint, Constraint, Constraint]:
    """Hatayama Hatch's stamina, attack and defense at the most it reads."""
    return (
        Constraint.exactly(TOP_STAMINA * HUNDRED),
        Constraint.exactly(HATAYAMA_TOP_STAT * HUNDRED),
        Constraint.exactly(HATAYAMA_TOP_STAT * HUNDRED),
    )


KINDS: Final[dict[Device, Callable[[], tuple[GameCheat, ...]]]] = {
    Device.DATACH_ULTRAMAN: lambda: (
        GameCheat("items", "Every item at the top", "アイテム ぜんぶ さいだい", _ultraman_items),
    ),
    Device.DATACH_SD_GUNDAM: lambda: (
        _numbered(Device.DATACH_SD_GUNDAM, "GHP", "Most HP", "HP が いちばん おおい"),
        _numbered(Device.DATACH_SD_GUNDAM, "AP", "Most AP", "AP が いちばん おおい"),
        _numbered(Device.DATACH_SD_GUNDAM, "GDP", "Most DP", "DP が いちばん おおい"),
    ),
    Device.DATACH_YUYU: lambda: (
        _items(
            Device.DATACH_YUYU, "level", "Every item at its top level", "アイテム ぜんぶ さいだい"
        ),
    ),
    Device.BARCODE_WORLD: lambda: (_warrior(Device.BARCODE_WORLD, _c0_tops(), job=True),),
    Device.SENKI: lambda: (_warrior(Device.SENKI, _c0_tops(), job=True),),
    Device.HATAYAMA: lambda: (_warrior(Device.HATAYAMA, _hatayama_tops(), job=False),),
    **{device: (lambda device=device: _effects(device)) for device in EFFECT_GAMES},
    Device.EXCITE95: lambda: (
        _items(Device.EXCITE95, "value", "Every item at its top", "アイテム ぜんぶ さいだい"),
    ),
    Device.EXCITE94: lambda: (
        GameCheat("keeper", "Best keeper", "いちばんの キーパー", _keeper),
        _items(Device.EXCITE94, "value", "Every item at its top", "アイテム ぜんぶ さいだい"),
    ),
    Device.DATACH_BATTLE_RUSH: lambda: tuple(
        GameCheat(stat, english, japanese, lambda stat=stat: _robot(stat))
        for stat, english, japanese in (
            ("attack", "Most attack", "こうげきが いちばん たかい"),
            ("defense", "Most defense", "ぼうぎょが いちばん たかい"),
            ("speed", "Most speed", "スピードが いちばん はやい"),
        )
    ),
    Device.BATTLE_SPACE: lambda: (
        _numbered(Device.BATTLE_SPACE, "GDP", "Most DP", "DP が いちばん おおい"),
        _numbered(Device.BATTLE_SPACE, "BMP", "Most MP", "MP が いちばん おおい"),
    ),
    Device.MONSTER_MAKER: lambda: tuple(
        GameCheat(key, english, japanese, lambda place=place: (_later_best(place),))
        for key, place, english, japanese in (
            ("ap", LATER_AP, "Most AP later in the game", "あとで AP が いちばん おおい"),
            ("mp", LATER_MP, "Most MP later in the game", "あとで MP が いちばん おおい"),
        )
    ),
    Device.KATTOBI: lambda: (
        GameCheat("torque", "Most torque", "トルクが いちばん おおきい", _torque),
    ),
    Device.FAMISTA3: lambda: (
        GameCheat(
            "average",
            "Best batting average",
            "だりつが いちばん たかい",
            lambda: _famista(BATTER, _average),
        ),
        GameCheat(
            "speed",
            "Fastest runner",
            "あしが いちばん はやい",
            lambda: _famista(BATTER, lambda card: value_of(card, "FSP")),
            "FSP",
        ),
        GameCheat(
            "era",
            "Lowest ERA",
            "ぼうぎょりつが いちばん いい",
            lambda: _famista(PITCHER, _earned_runs),
        ),
        GameCheat(
            "pitch",
            "Fastest pitch",
            "きゅうそくが いちばん はやい",
            lambda: _famista(PITCHER, lambda card: value_of(card, "FKM")),
            "FKM",
        ),
        GameCheat(
            "stamina",
            "Most stamina",
            "スタミナが いちばん おおい",
            lambda: _famista(PITCHER, lambda card: value_of(card, "FST")),
            "FST",
        ),
    ),
    Device.FAMJOCK2: lambda: (
        GameCheat(
            "mare",
            "Mare with 9 in every number",
            "ぜんぶ 9 の はんしょくば",
            lambda: _one(Device.FAMJOCK2, MARE),
        ),
        GameCheat(
            "stallion",
            "Stallion with 9 in every number",
            "ぜんぶ 9 の しゅぼば",
            lambda: _one(Device.FAMJOCK2, STALLION),
        ),
        GameCheat(
            "boxed",
            "A 10 from a Namco box bonus",
            "ナムコの はこで 10 に なる",
            lambda: (strongest_boxed(),),
        ),
    ),
    Device.BARDIGUN: lambda: (
        _numbered(Device.BARDIGUN, "DPW", "Most power", "ちからが いちばん つよい"),
        _numbered(Device.BARDIGUN, "DSM", "Most smarts", "あたまが いちばん いい"),
        _numbered(Device.BARDIGUN, "DSD", "Most speed", "はやさが いちばん はやい"),
    ),
}
"""Every game's kinds after its strongest card."""
