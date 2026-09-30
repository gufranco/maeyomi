"""The effect games and Excite Stage '95, served like every other game.

Each surface looks a game up in the dispatch table as a `DatachGame`. The
games whose codes set off one effect share one adapter, and Excite Stage
'95's item cards take their value as a pick rather than as a number to slide.
"""

from typing import Final

from maeyomi.datach.battlerush import (
    FRAME_CARD,
    RobotOrder,
    build_robot,
    decode_battlerush,
    strongest_robot,
)
from maeyomi.datach.game_card import DatachCard, GameKind, GameOption, GamePick
from maeyomi.datach.game_types import FIGHTING_KINDS, CardText, DatachGame, GameEntry, GameOrder
from maeyomi.games.alice import ALICE
from maeyomi.games.donald import DONALD
from maeyomi.games.doraemon2 import DORAEMON2
from maeyomi.games.doraemon3 import DORAEMON3
from maeyomi.games.dslayer2 import DSLAYER2
from maeyomi.games.effects import (
    EffectGame,
    build_effect,
    decode_effect,
    effect_of,
    screen_of,
    strongest_effect,
)
from maeyomi.games.excite94 import FIRST_ITEM as EXCITE94_FIRST_ITEM
from maeyomi.games.excite94 import ITEMS as EXCITE94_ITEMS
from maeyomi.games.excite94 import PK_ITEM_NAMES as EXCITE94_PK_ITEMS
from maeyomi.games.excite94 import (
    build_excite94_item,
    build_excite94_player,
    decode_excite94,
    pk_reading,
    strongest_excite94,
)
from maeyomi.games.excite94_players import PLAYERS
from maeyomi.games.excite95 import (
    HANDICAP,
    ITEMS,
    NO_CARDS,
    SPECIAL_VALUES,
    TOP_VALUE,
    build_excite95,
    decode_excite95,
    strongest_excite95,
)
from maeyomi.games.excite95 import PK_ITEM_NAMES as EXCITE95_PK_ITEMS
from maeyomi.games.excite95 import pk_reading as pk95_reading
from maeyomi.games.hatayama import (
    MP_KEY,
    TOP_MP,
    WARRIOR,
    WIZARD,
    HatayamaOrder,
    build_hatayama,
    decode_hatayama,
    strongest_hatayama,
)
from maeyomi.games.lupin import LUPIN
from maeyomi.games.spiderman import SPIDERMAN
from maeyomi.games.yousei import YOUSEI
from maeyomi.romaji import romanised
from maeyomi.said import Said

type Pair = tuple[str, str]

EFFECT: Final[Pair] = ("Effect", "こうか")
NO_EFFECT: Final[Pair] = ("No effect", "なにも おきない")
NOTHING_HAPPENS: Final[Pair] = (
    "The game reads it and nothing happens",
    "よみこむが なにも おきない",
)
VALUE_KEY: Final = "value"
ITEM_CARD: Final[Pair] = ("Item card for a match", "しあいの アイテム カード")
SPECIAL_CARD: Final[Pair] = ("Special item card", "とくしゅな アイテム カード")
SPECIAL_KINDS: Final = frozenset({HANDICAP, NO_CARDS})


def effect_game(game: EffectGame) -> DatachGame:
    """A game whose barcodes each set off one effect."""
    return DatachGame(
        decode=lambda code: decode_effect(code, game),
        build=lambda order: None if order.ident is None else build_effect(order.ident, game),
        strongest=lambda: strongest_effect(game),
        entries=lambda: tuple(
            GameEntry(effect.ident, GameKind.EFFECT, *effect.name) for effect in game.effects
        ),
        describe=lambda card: _effect_text(card, game),
        named=lambda typed: _effect_named(typed, game),
        stat_keys=(),
        datach_reader=False,
    )


def _effect_text(card: DatachCard, game: EffectGame) -> CardText:
    """What the effect is and does, and where the game reads the code."""
    effect = effect_of(card.ident, game)
    if effect is None:
        return CardText(NO_EFFECT, NOTHING_HAPPENS, EFFECT, game.screen)
    return CardText(effect.name, effect.detail, EFFECT, screen_of(effect, game))


def _effect_named(typed: str, game: EffectGame) -> int:
    """An effect typed by name or number, or a ValueError naming the game."""
    wanted = typed.strip().casefold()
    for effect in game.effects:
        english, japanese = effect.name
        if wanted in {english.casefold(), japanese, str(effect.ident)}:
            return effect.ident
    message = Said(
        f"unknown {game.device.english} effect {typed!r}; kinds lists them",
        f"{game.device.japanese}に {typed!r} という こうかは ない",
    )
    raise ValueError(message)


def _excite_values(kind: int) -> range:
    """The values an item of this kind can carry."""
    return SPECIAL_VALUES if kind in SPECIAL_KINDS else range(TOP_VALUE + 1)


def _excite_order(order: GameOrder) -> DatachCard | None:
    """An Excite Stage '95 item of the kind and value picked, the value at its top unless picked."""
    if order.ident is None:
        return None
    value = dict(order.picks).get(VALUE_KEY, _excite_values(order.ident)[-1])
    return build_excite95(order.ident, value)


def _excite_picks(kind: int) -> tuple[GamePick, ...]:
    """The value an item of this kind can take."""
    options = tuple(GameOption(value, str(value), str(value)) for value in _excite_values(kind))
    return (GamePick(VALUE_KEY, "Value", "あたい", options),)


def _excite_text(card: DatachCard) -> CardText:
    """The ability an item raises and by how much, or what a special card does."""
    (value,) = card.traits
    detail = SPECIAL_CARD if card.ident in SPECIAL_KINDS else ITEM_CARD
    pk_english, pk_japanese = EXCITE95_PK_ITEMS[pk95_reading(card.barcode)[0]]
    power = (
        f"Raises it by {value}; in PK mode {pk_english.lower()} +1",
        f"{value} あがる・PKモードでは {pk_japanese} +1",
    )
    return CardText(ITEMS[card.ident], detail, EFFECT, power)


def _excite_named(typed: str) -> int:
    """An item typed by name or number, or a ValueError naming the game."""
    wanted = typed.strip().casefold()
    for kind, (english, japanese) in ITEMS.items():
        if wanted in {english.casefold(), japanese, str(kind)}:
            return kind
    message = Said(
        f"unknown J.League Excite Stage '95 item {typed!r}; kinds lists them",
        f"J.リーグエキサイトステージ'95に {typed!r} という アイテムは ない",
    )
    raise ValueError(message)


CLASSES: Final[dict[int, Pair]] = {
    WARRIOR: ("Warrior", "せんし"),
    WIZARD: ("Wizard", "まほうつかい"),
}
REFUSED: Final[Pair] = ("Refused", "よみこまない")
TYPE_FIVE: Final[Pair] = ("A type of 5 or more", "タイプが 5いじょう")
STRATEGY: Final[Pair] = ("Strategy", "さくせん")
STRATEGIES: Final[tuple[Pair, ...]] = (
    ("Blizzard", "ブリザード"),
    ("Multiball", "マルチボール"),
    ("Earthquake", "じしん"),
    ("Thunder", "かみなり"),
    ("Hurricane", "ハリケーン"),
    ("Mist", "きり"),
)


def _hatayama_order(order: GameOrder) -> DatachCard | None:
    """A Hatayama Hatch battler: its numbers are stamina, attack and defense."""
    ident = WARRIOR if order.ident is None else order.ident
    return build_hatayama(HatayamaOrder(ident, order.stats, order.picks))


def _hatayama_picks(ident: int) -> tuple[GamePick, ...]:
    """A wizard's magic; a warrior has none."""
    if ident != WIZARD:
        return ()
    options = tuple(GameOption(value, str(value), str(value)) for value in range(TOP_MP + 1))
    return (GamePick(MP_KEY, "Magic", "まほう", options),)


def _hatayama_text(card: DatachCard) -> CardText:
    """A battler's class and type, and the strategy and graphic its last digit picks."""
    kind, strategy, graphic = card.traits
    english, japanese = STRATEGIES[strategy]
    power = (f"{english}; graphic {graphic + 1}", f"{japanese}、え {graphic + 1}")
    if card.kind is GameKind.NO_EFFECT:
        return CardText(REFUSED, TYPE_FIVE, STRATEGY, power)
    return CardText(CLASSES[card.ident], (f"Type {kind}", f"タイプ {kind}"), STRATEGY, power)


def _hatayama_named(typed: str) -> int:
    """A class typed by name or number, or a ValueError naming the two."""
    wanted = typed.strip().casefold()
    for ident, (english, japanese) in CLASSES.items():
        if wanted in {english.casefold(), japanese, str(ident)}:
            return ident
    message = Said(
        f"unknown Hatayama Hatch class {typed!r}; choose warrior or wizard",
        f"はた山ハッチに {typed!r} という クラスは ない。せんしか まほうつかいを えらんで",
    )
    raise ValueError(message)


FIELD_PLAYER: Final[Pair] = ("Hidden field player", "かくし せんしゅ")
KEEPER: Final[Pair] = ("Hidden keeper", "かくし キーパー")
GRADES: Final[Pair] = ("Grades", "ランク")
GRADE_LETTERS: Final = "ABCDEFGHI"


def _excite94_order(order: GameOrder) -> DatachCard | None:
    """A hidden player, or an item of the kind and value picked."""
    if order.ident is None:
        return None
    if order.ident < EXCITE94_FIRST_ITEM:
        return build_excite94_player(order.ident)
    value = dict(order.picks).get(VALUE_KEY, TOP_VALUE)
    return build_excite94_item(order.ident - EXCITE94_FIRST_ITEM, value)


def _excite94_picks(ident: int) -> tuple[GamePick, ...]:
    """An item's value; a player carries none."""
    return () if ident < EXCITE94_FIRST_ITEM else _excite_picks(ident - EXCITE94_FIRST_ITEM)


def _excite94_text(card: DatachCard) -> CardText:
    """A player's name and grades, or an item's ability and how far it raises it."""
    if card.kind is GameKind.ITEM:
        (value,) = card.traits
        name = EXCITE94_ITEMS[card.ident - EXCITE94_FIRST_ITEM]
        pk_type, level = pk_reading(card.barcode)
        pk_english, pk_japanese = EXCITE94_PK_ITEMS[pk_type]
        power = (
            f"Raises it by {value}; in PK mode {pk_english.lower()}, level {level}",
            f"{value} あがる・PKモードでは {pk_japanese} レベル{level}",
        )
        return CardText(name, ITEM_CARD, EFFECT, power)
    name, grades = PLAYERS[card.ident]
    (keeper,) = card.traits
    letters = [GRADE_LETTERS[int(nibble, 16)] for nibble in grades]
    shown = (
        (f"DEF {letters[2]}", f"ディフェンス {letters[2]}")
        if keeper
        else (
            f"KIC {letters[2]}, SHT {letters[3]}, RUN {letters[4]}, DRB {letters[5]}",
            f"キック {letters[2]}・シュート {letters[3]}・ラン {letters[4]}・ドリブル {letters[5]}",
        )
    )
    return CardText((romanised(name), name), KEEPER if keeper else FIELD_PLAYER, GRADES, shown)


def _excite94_named(typed: str) -> int:
    """A player or item typed by name or number, or a ValueError naming the game."""
    wanted = typed.strip().casefold()
    named = {
        **{ident: (romanised(name), name) for ident, (name, _) in PLAYERS.items()},
        **{EXCITE94_FIRST_ITEM + kind: names for kind, names in EXCITE94_ITEMS.items()},
    }
    for ident, (english, japanese) in named.items():
        if wanted in {english.casefold(), japanese, str(ident)}:
            return ident
    message = Said(
        f"unknown J.League Excite Stage '94 card {typed!r}; kinds lists them",
        f"J.リーグエキサイトステージ'94に {typed!r} という カードは ない",
    )
    raise ValueError(message)


def _excite94_entries() -> tuple[GameEntry, ...]:
    """Every hidden player a code reaches, then the five items."""
    players = tuple(
        GameEntry(ident, GameKind.PLAYER, romanised(name), name)
        for ident, (name, _) in PLAYERS.items()
        if build_excite94_player(ident) is not None
    )
    items = tuple(
        GameEntry(EXCITE94_FIRST_ITEM + kind, GameKind.ITEM, *names)
        for kind, names in EXCITE94_ITEMS.items()
    )
    return (*players, *items)


ROBOTS: Final = 64
PART_PICKS: Final = (
    ("head", "Head", "あたま"),
    ("body", "Body", "からだ"),
    ("shoulder", "Shoulder", "かた"),
    ("foot", "Foot", "あし"),
)
LEVEL_PICKS: Final = (
    ("recovery", "Recovery level", "かいふく レベル"),
    ("defense", "Defense level", "ぼうぎょ レベル"),
    ("attack", "Attack level", "こうげき レベル"),
    ("speed", "Speed level", "スピード レベル"),
)
PARTS: Final = 32
LEVELS: Final = 8
PILOTS: Final = 16
WEAPONS: Final = 64
OPPONENTS: Final[dict[int, str]] = {
    0: "Y・ミヤーン / ブロッコリィ",
    1: "LB・タイセイ / ダイゼイン",
    2: "F・シャドウ / ムッチーQ",
    3: "T・バンブー / ハナーン",
    4: "S・ナウストーン / ハンマーブレード",
    5: "O・ヒロタケ / バイザーナックル",
    6: "A・ヒラマツ / レーザークロウ",
    7: "R・タカオカ / ルオウ",
    8: "K・イマーイン / アドン",
    9: "SID2800 / ゴーリキー",
    10: "E・キヨハラ / きよひめS-3",
    11: "I・ノーマ / コブラキャノン",
    12: "ミスターX / ボンボンR-01",
    13: "ミスターB / ボンボンR-02",
    14: "ミスターD / ボンボンR-03",
    15: "ミスターM / ボンボンR-04",
}
"""The pilot and robot MAME showed for each number the game names; the rest go unnamed."""
FRAME_TEXT: Final[Pair] = ("Frame card: scan it first", "1まいめに よませる")
WEAPON_TEXT: Final[Pair] = ("Weapon card: scan it second", "2まいめに よませる")
PARTS_HEADING: Final[Pair] = ("Parts", "パーツ")
LEVELS_HEADING: Final[Pair] = ("Levels", "レベル")
SHOP_CODE: Final[Pair] = (
    "A shop barcode or an unmarked code",
    "おみせの バーコードか しるしの ない コード",
)


def _robot_name(ident: int) -> Pair:
    """An opponent's names, or the robot's number."""
    name = OPPONENTS.get(ident)
    return (romanised(name), name) if name else (f"Robot {ident}", f"ロボット {ident}")


def _robot_order(order: GameOrder) -> RobotOrder:
    """The robot a game order asks for, parts and levels from its picks."""
    picks = dict(order.picks)
    return RobotOrder(
        ident=order.ident or 0,
        head=picks.get("head", 0),
        body=picks.get("body", 0),
        shoulder=picks.get("shoulder", 0),
        foot=picks.get("foot", 0),
        pilot=picks.get("pilot", 0),
        weapons=(picks.get("weapon", 0), picks.get("second_weapon", 0)),
        levels=(
            picks.get("recovery", 0),
            picks.get("defense", 0),
            picks.get("attack", 0),
            picks.get("speed", 0),
        ),
    )


def _robot_card(order: GameOrder, which: int) -> DatachCard | None:
    """One card of the robot ordered: 0 the frame, 1 the weapons."""
    pair = build_robot(_robot_order(order))
    return None if pair is None else pair[which]


def _robot_picks(_: int) -> tuple[GamePick, ...]:
    """The parts, pilot, weapons and levels any robot takes."""

    def numbered(key: str, english: str, japanese: str, count: int) -> GamePick:
        options = tuple(GameOption(value, str(value), str(value)) for value in range(count))
        return GamePick(key, english, japanese, options)

    return (
        *(numbered(key, english, japanese, PARTS) for key, english, japanese in PART_PICKS),
        numbered("pilot", "Pilot type", "パイロット", PILOTS),
        numbered("weapon", "Weapon", "ぶき", WEAPONS),
        numbered("second_weapon", "Second weapon", "2つめの ぶき", WEAPONS),
        *(numbered(key, english, japanese, LEVELS) for key, english, japanese in LEVEL_PICKS),
    )


def _robot_text(card: DatachCard) -> CardText:
    """A frame card's parts, a weapon card's levels, or why a code is refused."""
    if card.kind is GameKind.NO_EFFECT:
        return CardText(REFUSED, SHOP_CODE, PARTS_HEADING, SHOP_CODE)
    if card.traits[0] == FRAME_CARD:
        _, _, head, body, shoulder, foot, pilot, _ = card.traits
        parts = (
            f"Head {head}, body {body}, shoulder {shoulder}, foot {foot}, pilot {pilot}",
            f"あたま {head}・からだ {body}・かた {shoulder}・あし {foot}・パイロット {pilot}",
        )
        return CardText(_robot_name(card.ident), FRAME_TEXT, PARTS_HEADING, parts)
    recovery, defense, attack, speed = card.traits[-4:]
    levels = (
        f"Recovery {recovery}, defense {defense}, attack {attack}, speed {speed}",
        f"かいふく {recovery}・ぼうぎょ {defense}・こうげき {attack}・スピード {speed}",
    )
    return CardText(_robot_name(card.ident), WEAPON_TEXT, LEVELS_HEADING, levels)


def _robot_named(typed: str) -> int:
    """A robot typed by an opponent's name or its number."""
    wanted = typed.strip().casefold()
    for ident in range(ROBOTS):
        english, japanese = _robot_name(ident)
        if wanted == str(ident) or any(
            wanted in {english_part.strip().casefold(), japanese_part.strip().casefold()}
            for english_part, japanese_part in zip(
                [english, *english.split("/")], [japanese, *japanese.split("/")], strict=True
            )
        ):
            return ident
    message = Said(
        f"unknown Datach Battle Rush robot {typed!r}; choose 0 to 63 or an opponent's name",
        f"バトルラッシュに {typed!r} という ロボットは ない。0から63か、あいての なまえに して",
    )
    raise ValueError(message)


EFFECT_GAMES: Final = {
    game.device: effect_game(game)
    for game in (LUPIN, DONALD, SPIDERMAN, ALICE, DORAEMON2, DORAEMON3, YOUSEI, DSLAYER2)
}
EXCITE95_GAME: Final = DatachGame(
    decode=decode_excite95,
    build=_excite_order,
    strongest=strongest_excite95,
    entries=lambda: tuple(GameEntry(kind, GameKind.ITEM, *names) for kind, names in ITEMS.items()),
    describe=_excite_text,
    named=_excite_named,
    stat_keys=(),
    picks=_excite_picks,
    datach_reader=False,
    drawable=FIGHTING_KINDS | {GameKind.ITEM},
)
HATAYAMA_GAME: Final = DatachGame(
    decode=decode_hatayama,
    build=_hatayama_order,
    strongest=strongest_hatayama,
    entries=lambda: tuple(
        GameEntry(ident, GameKind.FIGHTER, *names) for ident, names in CLASSES.items()
    ),
    describe=_hatayama_text,
    named=_hatayama_named,
    stat_keys=("WHP", "WST", "WDF"),
    picks=_hatayama_picks,
    datach_reader=False,
)
EXCITE94_GAME: Final = DatachGame(
    decode=decode_excite94,
    build=_excite94_order,
    strongest=strongest_excite94,
    entries=_excite94_entries,
    describe=_excite94_text,
    named=_excite94_named,
    stat_keys=(),
    picks=_excite94_picks,
    datach_reader=False,
    drawable=FIGHTING_KINDS | {GameKind.ITEM},
)
BATTLE_RUSH_GAME: Final = DatachGame(
    decode=decode_battlerush,
    build=lambda order: _robot_card(order, 0),
    strongest=lambda: strongest_robot()[0],
    entries=lambda: tuple(
        GameEntry(ident, GameKind.UNIT, *_robot_name(ident)) for ident in range(ROBOTS)
    ),
    describe=_robot_text,
    named=_robot_named,
    stat_keys=(),
    picks=_robot_picks,
    drawable=frozenset({GameKind.UNIT}),
    companion=lambda order: _robot_card(order, 1),
    strongest_companion=lambda: strongest_robot()[1],
)
