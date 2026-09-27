"""The web page's device switch: read, build and cheat for any device or game.

The Barcode Battler II keeps its own routes, which know its nearest-match
search. Every other device goes through here, calling the same decoders,
solvers and cheat searches the command line calls, so the two surfaces give
the same card for the same request.

What a card is gets described from the face it prints, so the page and the
paper cannot say different things about one barcode.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.bb1.solve import MAX_HP as FIRST_MAX_HP
from maeyomi.bb1.solve import MAX_STAT as FIRST_MAX_STAT
from maeyomi.datach.dbz import BONUS, UNIT
from maeyomi.datach.dbz_names import FIGHTERS, ITEMS
from maeyomi.datach.dbz_solve import (
    MAX_HALVED,
    MAX_HP,
)
from maeyomi.double.solve import MAX_VALUE as DOUBLE_MAX
from maeyomi.models.device import Device
from maeyomi.models.generated_card import CardResult
from maeyomi.rendering.face import face_of
from maeyomi.rendering.labels import SPECIAL_POWER, STAT_LABELS, Bilingual
from maeyomi.ui.schemas import DbzChoiceView, DeviceView, FactView

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
"""Where most Dragon Ball Z fighters sit: 80 percent of random codes fall inside these."""


@dataclass(frozen=True, slots=True)
class DeviceForm:
    """Which parts of the card maker a device reads, and how far each number goes."""

    fields: tuple[str, ...]
    hp_max: int
    st_max: int
    df_max: int
    steps: tuple[int, int, int] = (HUNDREDS, HUNDREDS, HUNDREDS)
    stat_keys: tuple[str, ...] = tuple(CLASSIC_STATS)
    sheet_fields: tuple[str, ...] = ()
    ranges: tuple[Range, Range, Range] = CLASSIC_RANGES


FORMS: Final[dict[Device, DeviceForm]] = {
    Device.BB2: DeviceForm(
        ("race", "class", "ability", "speed", "job", "backRead", "nearest"),
        SECOND_MAX_HP,
        SECOND_MAX_STAT,
        SECOND_MAX_STAT,
        sheet_fields=("race",),
    ),
    Device.BB1: DeviceForm(
        ("race", "job", "backRead"),
        FIRST_MAX_HP,
        FIRST_MAX_STAT,
        FIRST_MAX_STAT,
        sheet_fields=("race",),
    ),
    Device.DOUBLE: DeviceForm(("job",), DOUBLE_MAX, DOUBLE_MAX, DOUBLE_MAX),
    Device.DATACH_DBZ: DeviceForm(
        ("dbz", "nearest"),
        MAX_HP,
        MAX_HALVED,
        MAX_HALVED,
        (HP_STEP, HALVED_STEP, HALVED_STEP),
        ("stat.hp", "stat.bp", "stat.dp"),
        ranges=DBZ_RANGES,
    ),
}


def device_views() -> list[DeviceView]:
    """Every device, in the order the enum lists them, with its form."""
    return [
        DeviceView(
            key=device.value,
            english=device.english,
            japanese=device.japanese,
            group="game" if device.is_game else "machine",
            fields=list(FORMS[device].fields),
            hp_max=FORMS[device].hp_max,
            st_max=FORMS[device].st_max,
            df_max=FORMS[device].df_max,
            steps=list(FORMS[device].steps),
            stat_keys=list(FORMS[device].stat_keys),
            sheet_fields=list(FORMS[device].sheet_fields),
            ranges=[list(bounds) for bounds in FORMS[device].ranges],
        )
        for device in Device
    ]


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
