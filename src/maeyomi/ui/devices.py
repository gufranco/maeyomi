"""The web page's device switch: read, build and cheat for any device or game.

The Barcode Battler II keeps its own routes, which know its nearest-match
search. Every other device goes through here, calling the same decoders,
solvers and cheat searches the command line calls, so the two surfaces give
the same card for the same request.

What a card is gets described from the face it prints, so the page and the
paper cannot say different things about one barcode.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from maeyomi.barcode.geometry import symbology_of
from maeyomi.bb1.solve import ENEMY_DF, ENEMY_HP, ENEMY_ST
from maeyomi.bb1.solve import MAX_HP as FIRST_MAX_HP
from maeyomi.bb1.solve import MAX_STAT as FIRST_MAX_STAT
from maeyomi.cheat_kinds import cheat_kinds, kind_name
from maeyomi.datach.dbz import BONUS, UNIT
from maeyomi.datach.dbz_names import FIGHTERS, ITEMS
from maeyomi.datach.dbz_solve import (
    MAX_HALVED,
    MAX_HP,
)
from maeyomi.datach.games import game_for
from maeyomi.datach.sdgundam_tables import AP_BONUS, BASES, DP_BONUS, HP_BONUS
from maeyomi.datach.ultraman import HUNDRED, STRONGEST_HUNDREDS
from maeyomi.decoder.back_read import fighter_limits
from maeyomi.double.solve import MAX_VALUE as DOUBLE_MAX
from maeyomi.games.barcode_world import TOP_HP, TOP_STAT
from maeyomi.games.hatayama import TOP_STAMINA
from maeyomi.games.hatayama import TOP_STAT as HATAYAMA_TOP_STAT
from maeyomi.generator.device_random import holds_ranges
from maeyomi.models.device import Device
from maeyomi.models.generated_card import CardResult
from maeyomi.rendering.face import face_of
from maeyomi.rendering.labels import SPECIAL_POWER, STAT_LABELS, Bilingual
from maeyomi.ui.schemas import (
    CheatKindView,
    DbzChoiceView,
    DeviceView,
    FactView,
    OptionView,
    PickView,
)

HUNDREDS: Final = 100
HP_STEP: Final = BONUS * UNIT
HALVED_STEP: Final = HP_STEP // 2
SECOND_MAX_HP: Final = 99900
SECOND_MAX_STAT: Final = 19900
CLASSIC_STATS: Final = ["stat.hp", "stat.st", "stat.df"]
KIND: Final = Bilingual("Kind", "しゅるい")
DETAIL: Final = Bilingual("Type", "タイプ")


type Range = tuple[int, int]

CLASSIC_RANGES: Final[tuple[Range, Range, Range]] = ((1000, 10000), (100, 3000), (100, 3000))
DBZ_RANGES: Final[tuple[Range, Range, Range]] = ((10000, 60000), (5000, 30000), (5000, 30000))
BATTLE_SPACE_RANGES: Final[tuple[Range, Range, Range]] = (
    (100, 999900),
    (100, 99900),
    (100, 99900),
)
"""Where most Dragon Ball Z fighters sit: 80 percent of random codes fall inside these."""
ULTRAMAN_MAX: Final = STRONGEST_HUNDREDS * HUNDRED
ULTRAMAN_RANGES: Final[tuple[Range, Range, Range]] = (
    (0, ULTRAMAN_MAX),
    (0, ULTRAMAN_MAX),
    (0, ULTRAMAN_MAX),
)
GUNDAM_STEP: Final = 10
YUYU_MAX: Final = 9999
WORLD_MAX_HP: Final = TOP_HP * HUNDRED
WORLD_MAX_STAT: Final = TOP_STAT * HUNDRED
HATAYAMA_MAX_HP: Final = TOP_STAMINA * HUNDRED
HATAYAMA_MAX_STAT: Final = HATAYAMA_TOP_STAT * HUNDRED
BATTLE_SPACE_MAX_HP: Final = 999900
BATTLE_SPACE_MAX_STAT: Final = 99900


def _gundam_range(index: int, bonus: tuple[int, ...]) -> Range:
    """The lowest base and the highest base plus the top bonus, of one number."""
    return min(base[index] for base in BASES), max(base[index] for base in BASES) + max(bonus)


GUNDAM_RANGES: Final[tuple[Range, Range, Range]] = (
    _gundam_range(0, HP_BONUS),
    _gundam_range(1, AP_BONUS),
    _gundam_range(2, DP_BONUS),
)


@dataclass(frozen=True, slots=True)
class DeviceForm:
    """Which parts of the card maker a device reads, and how far each number goes."""

    fields: tuple[str, ...]
    hp_max: int
    st_max: int
    df_max: int
    steps: tuple[int, int, int] = (HUNDREDS, HUNDREDS, HUNDREDS)
    stat_keys: tuple[str, ...] = tuple(CLASSIC_STATS)
    sheet_fields: tuple[str, ...] = ("third",)
    ranges: tuple[Range, Range, Range] = CLASSIC_RANGES
    back_ranges: tuple[Range, Range, Range] | None = None


FORMS: Final[dict[Device, DeviceForm]] = {
    Device.BB2: DeviceForm(
        ("race", "class", "ability", "speed", "job", "backRead", "stats", "nearest"),
        SECOND_MAX_HP,
        SECOND_MAX_STAT,
        SECOND_MAX_STAT,
        sheet_fields=("race", "third"),
        back_ranges=fighter_limits(),
    ),
    Device.BB1: DeviceForm(
        ("race", "job", "backRead", "stats"),
        FIRST_MAX_HP,
        FIRST_MAX_STAT,
        FIRST_MAX_STAT,
        sheet_fields=("race", "third"),
        back_ranges=(ENEMY_HP, ENEMY_ST, ENEMY_DF),
    ),
    Device.DOUBLE: DeviceForm(("job", "stats"), DOUBLE_MAX, DOUBLE_MAX, DOUBLE_MAX),
    Device.DATACH_DBZ: DeviceForm(
        ("dbz", "stats", "nearest"),
        MAX_HP,
        MAX_HALVED,
        MAX_HALVED,
        (HP_STEP, HALVED_STEP, HALVED_STEP),
        ("stat.hp", "stat.bp", "stat.dp"),
        ranges=DBZ_RANGES,
    ),
    Device.DATACH_ULTRAMAN: DeviceForm(
        ("game", "stats"),
        ULTRAMAN_MAX,
        ULTRAMAN_MAX,
        ULTRAMAN_MAX,
        stat_keys=("stat.pw", "stat.ust", "stat.usp"),
        ranges=ULTRAMAN_RANGES,
    ),
    Device.DATACH_YUYU: DeviceForm(
        ("game", "picks"),
        YUYU_MAX,
        YUYU_MAX,
        YUYU_MAX,
        stat_keys=("stat.yhp", "stat.ysp", "stat.ysp"),
        sheet_fields=(),
        ranges=((0, YUYU_MAX), (0, YUYU_MAX), (0, YUYU_MAX)),
    ),
    Device.BARCODE_WORLD: DeviceForm(
        ("game", "picks", "stats"),
        WORLD_MAX_HP,
        WORLD_MAX_STAT,
        WORLD_MAX_STAT,
        stat_keys=("stat.whp", "stat.wst", "stat.wdf"),
        ranges=((1000, 19900), (100, 9900), (100, 9900)),
    ),
    Device.SENKI: DeviceForm(
        ("game", "picks", "stats"),
        WORLD_MAX_HP,
        WORLD_MAX_STAT,
        WORLD_MAX_STAT,
        stat_keys=("stat.whp", "stat.wst", "stat.wdf"),
        ranges=((1000, 19900), (100, 9900), (100, 9900)),
    ),
    Device.DATACH_JLEAGUE: DeviceForm(
        ("game",),
        YUYU_MAX,
        YUYU_MAX,
        YUYU_MAX,
        sheet_fields=(),
    ),
    Device.DATACH_SD_GUNDAM: DeviceForm(
        ("game", "picks", "stats"),
        GUNDAM_RANGES[0][1],
        GUNDAM_RANGES[1][1],
        GUNDAM_RANGES[2][1],
        (GUNDAM_STEP, GUNDAM_STEP, GUNDAM_STEP),
        ("stat.hp", "stat.ap", "stat.gdp"),
        ranges=GUNDAM_RANGES,
    ),
    **{
        device: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=())
        for device in (
            Device.LUPIN,
            Device.DONALD,
            Device.SPIDERMAN,
            Device.ALICE,
            Device.DORAEMON2,
            Device.DORAEMON3,
            Device.YOUSEI,
            Device.DSLAYER2,
        )
    },
    Device.EXCITE95: DeviceForm(("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.EXCITE94: DeviceForm(("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.DATACH_BATTLE_RUSH: DeviceForm(
        ("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()
    ),
    Device.BATTLE_SPACE: DeviceForm(
        ("game", "stats"),
        BATTLE_SPACE_MAX_HP,
        BATTLE_SPACE_MAX_STAT,
        BATTLE_SPACE_MAX_STAT,
        stat_keys=("stat.hp", "stat.ap", "stat.gdp"),
        sheet_fields=(),
        ranges=BATTLE_SPACE_RANGES,
    ),
    Device.MONSTER_MAKER: DeviceForm(
        ("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()
    ),
    Device.KATTOBI: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.FAMISTA3: DeviceForm(("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.FAMJOCK2: DeviceForm(("game", "picks"), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.BARDIGUN: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.CARD_DE_ASOBU: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.OSHARE_MAJO: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.MUSHIKING: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.WANTAME: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.ROCKMAN_DRAGON: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.DENSHA: DeviceForm(("game",), YUYU_MAX, YUYU_MAX, YUYU_MAX, sheet_fields=()),
    Device.HATAYAMA: DeviceForm(
        ("game", "picks", "stats"),
        HATAYAMA_MAX_HP,
        HATAYAMA_MAX_STAT,
        HATAYAMA_MAX_STAT,
        stat_keys=("stat.whp", "stat.wst", "stat.wdf"),
        ranges=((1000, 19900), (100, 9900), (100, 9900)),
    ),
}


class Platform(StrEnum):
    """What a device is, or which console a game with a reader runs on."""

    MACHINE = "machine"
    DATACH = "datach"
    FAMICOM = "famicom"
    SUPER_FAMICOM = "super_famicom"
    GAME_BOY = "game_boy"
    NINTENDO_DS = "nintendo_ds"
    BEENA = "beena"


DATACH_PREFIX: Final = "DATACH_"
FAMICOM_GAMES: Final = frozenset({Device.BARCODE_WORLD})
GAME_BOY_GAMES: Final = frozenset(
    {
        Device.BATTLE_SPACE,
        Device.MONSTER_MAKER,
        Device.KATTOBI,
        Device.FAMISTA3,
        Device.FAMJOCK2,
        Device.BARDIGUN,
    }
)
NINTENDO_DS_GAMES: Final = frozenset(
    {
        Device.CARD_DE_ASOBU,
        Device.OSHARE_MAJO,
        Device.MUSHIKING,
        Device.WANTAME,
        Device.ROCKMAN_DRAGON,
    }
)
BEENA_GAMES: Final = frozenset({Device.DENSHA})


def platform_of(device: Device) -> Platform:
    """The platform a device is listed under on the page."""
    if not device.is_game:
        return Platform.MACHINE
    if device.name.startswith(DATACH_PREFIX):
        return Platform.DATACH
    if device in GAME_BOY_GAMES:
        return Platform.GAME_BOY
    if device in NINTENDO_DS_GAMES:
        return Platform.NINTENDO_DS
    if device in BEENA_GAMES:
        return Platform.BEENA
    return Platform.FAMICOM if device in FAMICOM_GAMES else Platform.SUPER_FAMICOM


def device_views() -> list[DeviceView]:
    """Every device, in the order the enum lists them, with its form."""
    return [
        DeviceView(
            key=device.value,
            english=device.english,
            japanese=device.japanese,
            group="game" if device.is_game else "machine",
            platform=platform_of(device).value,
            fields=list(FORMS[device].fields),
            hp_max=FORMS[device].hp_max,
            st_max=FORMS[device].st_max,
            df_max=FORMS[device].df_max,
            steps=list(FORMS[device].steps),
            stat_keys=list(FORMS[device].stat_keys),
            sheet_fields=list(FORMS[device].sheet_fields),
            ranges=[list(bounds) for bounds in FORMS[device].ranges],
            back_ranges=_listed(FORMS[device].back_ranges),
            cheat_kinds=[
                CheatKindView(
                    key=kind.key,
                    english=kind.english,
                    japanese=kind.japanese,
                    default_name=kind_name(device, kind),
                )
                for kind in cheat_kinds(device)
            ],
            symbology=symbology_of(device).value,
            ranged=holds_ranges(device),
        )
        for device in Device
    ]


def _listed(ranges: tuple[Range, Range, Range] | None) -> list[list[int]] | None:
    """Ranges as the JSON lists the page reads, or None when there are none."""
    return None if ranges is None else [list(bounds) for bounds in ranges]


def dbz_choices() -> list[DbzChoiceView]:
    """Every fighter, then every item, Datach Dragon Ball Z can produce."""
    fighters = [
        DbzChoiceView(id=key, kind="fighter", english=english, japanese=japanese)
        for key, (english, japanese) in FIGHTERS.items()
    ]
    items = [
        DbzChoiceView(id=key, kind="item", english=item.english, japanese=item.japanese)
        for key, item in ITEMS.items()
    ]
    return fighters + items


def game_choices(device: Device) -> list[DbzChoiceView]:
    """Every card a Datach game after Dragon Ball Z can read, or none for any other device."""
    game = game_for(device)
    if game is None:
        return []
    return [
        DbzChoiceView(
            id=entry.ident, kind=entry.kind.value, english=entry.english, japanese=entry.japanese
        )
        for entry in game.entries()
    ]


def game_picks(device: Device, ident: int) -> list[PickView]:
    """The choices a game's card offers beside its numbers, such as a unit's weapons."""
    game = game_for(device)
    if game is None:
        return []
    return [
        PickView(
            key=pick.key,
            english=pick.english,
            japanese=pick.japanese,
            options=[
                OptionView(value=option.value, english=option.english, japanese=option.japanese)
                for option in pick.options
            ],
        )
        for pick in game.picks(ident)
    ]


def facts_of(result: CardResult) -> list[FactView]:
    """What a card is, line by line, taken from the face it prints."""
    face = face_of(result)
    heading = face.power_heading or Bilingual(
        f"{SPECIAL_POWER.english} {face.power_code:02d}", SPECIAL_POWER.japanese
    )
    tiles = [
        _fact(STAT_LABELS[tile.key], Bilingual(str(tile.value), str(tile.value)))
        for tile in face.tiles
    ]
    return [
        _fact(KIND, face.kind),
        _fact(DETAIL, face.detail),
        *tiles,
        _fact(heading, face.power_text),
    ]


def _fact(label: Bilingual, value: Bilingual) -> FactView:
    """One line of facts in both languages."""
    return FactView(
        label=label.english, label_ja=label.japanese, value=value.english, value_ja=value.japanese
    )
