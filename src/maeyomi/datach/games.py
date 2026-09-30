"""The Datach games after Dragon Ball Z, each described the same way.

Every surface that serves a game, the registry, the command line, the web page
and the card faces, looks the game up here rather than branching on it, so a
game added to this table is a game every surface supports.
"""

from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, DatachGame, GameEntry, GameOrder
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
from maeyomi.gameboy.battlespace import STAT_KEYS as BATTLE_SPACE_STATS
from maeyomi.gameboy.battlespace import (
    battle_space_entries,
    battle_space_named,
    battle_space_text,
    build_battle_space,
    decode_battle_space,
    strongest_battle_space,
)
from maeyomi.gameboy.famista3 import STAT_KEYS as FAMISTA3_STATS
from maeyomi.gameboy.famista3 import (
    build_famista3,
    decode_famista3,
    famista3_entries,
    famista3_named,
    famista3_picks,
    famista3_text,
    strongest_famista3,
)
from maeyomi.gameboy.famjock2 import STAT_KEYS as FAMJOCK2_STATS
from maeyomi.gameboy.famjock2 import (
    build_famjock2,
    decode_famjock2,
    famjock2_entries,
    famjock2_named,
    famjock2_picks,
    famjock2_text,
    strongest_famjock2,
)
from maeyomi.gameboy.kattobi import STAT_KEYS as KATTOBI_STATS
from maeyomi.gameboy.kattobi import (
    build_kattobi,
    decode_kattobi,
    kattobi_entries,
    kattobi_named,
    kattobi_text,
    strongest_kattobi,
)
from maeyomi.gameboy.monstermaker import STAT_KEYS as MONSTER_MAKER_STATS
from maeyomi.gameboy.monstermaker import (
    build_monster_maker,
    decode_monster_maker,
    monster_maker_entries,
    monster_maker_named,
    monster_maker_picks,
    monster_maker_text,
    strongest_monster_maker,
)
from maeyomi.games.barcode_world import (
    MAGICIAN,
    WARRIOR,
    BarcodeWorldOrder,
    build_barcode_world,
    decode_barcode_world,
    strongest_barcode_world,
)
from maeyomi.games.barcode_world import picks_for as barcode_world_picks
from maeyomi.games.senki import (
    SenkiOrder,
    black_store_stats,
    build_senki,
    decode_senki,
    strongest_senki,
)
from maeyomi.games.served import (
    BATTLE_RUSH_GAME,
    EFFECT_GAMES,
    EXCITE94_GAME,
    EXCITE95_GAME,
    HATAYAMA_GAME,
)
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


CLASSES: Final[dict[int, Pair]] = {
    WARRIOR: ("Warrior", "せんし"),
    MAGICIAN: ("Magician", "まほうつかい"),
}
ITEM_KINDS: Final[dict[int, Pair]] = {
    5: ("Weapon, one use", "ぶき (1かい)"),
    6: ("Weapon", "ぶき"),
    7: ("Protector, one use", "ぼうぐ (1かい)"),
    8: ("Protector", "ぼうぐ"),
    9: ("Helper item", "おたすけ アイテム"),
}
ABILITY_HEADING: Final[Pair] = ("Ability", "とくしゅ のうりょく")
CARD_HEADING: Final[Pair] = ("Card", "カード")
SOUND_TEST: Final[Pair] = ("Sound test", "サウンドテスト")
OPENS_SOUND_TEST: Final[Pair] = (
    "Opens the sound test in either battle mode",
    "たいせん モード で サウンドテストを ひらく",
)
NO_CARD: Final[Pair] = ("None; the game makes no card of it", "なし。カードに ならない")
FIRST_MAGICIAN: Final = 7


def _barcode_world_order(order: GameOrder) -> DatachCard | None:
    """Build a Barcode World fighter: its numbers are HP, ST and DF."""
    return build_barcode_world(BarcodeWorldOrder(order.ident, order.stats, order.picks))


def _barcode_world_entries() -> tuple[GameEntry, ...]:
    """The two kinds of fighter a Barcode World card can be built as."""
    return tuple(GameEntry(ident, GameKind.FIGHTER, *names) for ident, names in CLASSES.items())


def _senki_order(order: GameOrder) -> DatachCard | None:
    """Build a Barcode Battler Senki fighter: its numbers are HP, ST and DF."""
    return build_senki(SenkiOrder(order.ident, order.stats, order.picks))


def _barcode_world_named(typed: str) -> int:
    """A Barcode World class typed by name or number."""
    return _class_named(typed, Device.BARCODE_WORLD)


def _senki_named(typed: str) -> int:
    """A Barcode Battler Senki class typed by name or number."""
    return _class_named(typed, Device.SENKI)


def _class_named(typed: str, device: Device) -> int:
    """A class typed by name or number, or a ValueError naming the two there are."""
    wanted = typed.strip().casefold()
    for ident, (english, japanese) in CLASSES.items():
        if wanted in {english.casefold(), japanese, str(ident)}:
            return ident
    message = f"unknown {device.english} fighter {typed!r}; choose warrior or magician"
    raise ValueError(message)


def _senki_text(card: DatachCard) -> CardText:
    """The sound test, or a card as Barcode World describes it plus what the Black Store reads."""
    if card.kind is GameKind.HIDDEN:
        return CardText(SOUND_TEST, OPENS_SOUND_TEST, CARD_HEADING, NO_CARD)
    text = _barcode_world_text(card)
    shop = black_store_stats(card.barcode)
    if shop is None:
        return text
    hp, st, df = shop
    english, japanese = text.power
    power = (
        f"{english}; Black Store HP {hp}, ST {st}, DF {df}",
        f"{japanese}・ブラックストア HP {hp} ST {st} DF {df}",
    )
    return CardText(text.name, text.detail, text.heading, power)


def _barcode_world_text(card: DatachCard) -> CardText:
    """A fighter's class, job, speed and ability number, or an item's kind and number."""
    job, speed, ability, number, *_ = card.traits
    if card.kind is GameKind.ITEM:
        return CardText(
            ITEM_KINDS[card.ident],
            ITEM,
            CARD_HEADING,
            (f"No. {number} in the game's list", f"ゲームの いちらんの {number}ばん"),
        )
    kind = CLASSES[MAGICIAN if job >= FIRST_MAGICIAN else WARRIOR]
    return CardText(
        kind,
        (f"Job {job}, speed {speed}", f"しょくぎょう {job}・すばやさ {speed}"),
        ABILITY_HEADING,
        (f"No. {ability}", f"{ability}ばん"),
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
    Device.BARCODE_WORLD: DatachGame(
        decode=decode_barcode_world,
        build=_barcode_world_order,
        strongest=strongest_barcode_world,
        entries=_barcode_world_entries,
        describe=_barcode_world_text,
        named=_barcode_world_named,
        stat_keys=("WHP", "WST", "WDF"),
        picks=barcode_world_picks,
        datach_reader=False,
    ),
    Device.SENKI: DatachGame(
        decode=decode_senki,
        build=_senki_order,
        strongest=strongest_senki,
        entries=_barcode_world_entries,
        describe=_senki_text,
        named=_senki_named,
        stat_keys=("WHP", "WST", "WDF"),
        picks=barcode_world_picks,
        datach_reader=False,
    ),
    **EFFECT_GAMES,
    Device.EXCITE95: EXCITE95_GAME,
    Device.HATAYAMA: HATAYAMA_GAME,
    Device.EXCITE94: EXCITE94_GAME,
    Device.DATACH_BATTLE_RUSH: BATTLE_RUSH_GAME,
    Device.BATTLE_SPACE: DatachGame(
        decode=decode_battle_space,
        build=build_battle_space,
        strongest=strongest_battle_space,
        entries=battle_space_entries,
        describe=battle_space_text,
        named=battle_space_named,
        stat_keys=BATTLE_SPACE_STATS,
        datach_reader=False,
    ),
    Device.MONSTER_MAKER: DatachGame(
        decode=decode_monster_maker,
        build=build_monster_maker,
        strongest=strongest_monster_maker,
        entries=monster_maker_entries,
        describe=monster_maker_text,
        named=monster_maker_named,
        stat_keys=MONSTER_MAKER_STATS,
        picks=monster_maker_picks,
        datach_reader=False,
    ),
    Device.KATTOBI: DatachGame(
        decode=decode_kattobi,
        build=build_kattobi,
        strongest=strongest_kattobi,
        entries=kattobi_entries,
        describe=kattobi_text,
        named=kattobi_named,
        stat_keys=KATTOBI_STATS,
        datach_reader=False,
    ),
    Device.FAMISTA3: DatachGame(
        decode=decode_famista3,
        build=build_famista3,
        strongest=strongest_famista3,
        entries=famista3_entries,
        describe=famista3_text,
        named=famista3_named,
        stat_keys=FAMISTA3_STATS,
        picks=famista3_picks,
        datach_reader=False,
    ),
    Device.FAMJOCK2: DatachGame(
        decode=decode_famjock2,
        build=build_famjock2,
        strongest=strongest_famjock2,
        entries=famjock2_entries,
        describe=famjock2_text,
        named=famjock2_named,
        stat_keys=FAMJOCK2_STATS,
        picks=famjock2_picks,
        datach_reader=False,
    ),
}


def game_for(device: Device) -> DatachGame | None:
    """The game a device is, or None for a machine and for Dragon Ball Z."""
    return GAMES.get(device)
