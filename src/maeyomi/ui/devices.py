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

from maeyomi.bb1.cheat import strongest_first_card
from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.solve import MAX_HP as FIRST_MAX_HP
from maeyomi.bb1.solve import MAX_STAT as FIRST_MAX_STAT
from maeyomi.bb1.solve import solve_first
from maeyomi.cli.double_device import NO_BACK_READ
from maeyomi.datach.dbz import BONUS, UNIT, decode_dbz
from maeyomi.datach.dbz_cheat import strongest_dbz_card
from maeyomi.datach.dbz_names import FIGHTERS, ITEMS, character_id
from maeyomi.datach.dbz_solve import (
    MAX_HALVED,
    MAX_HP,
    request_from,
    solve_dbz,
    solve_dbz_nearest,
    unread_fields,
)
from maeyomi.decoder.decode import decode
from maeyomi.double.cheat import strongest_double_card
from maeyomi.double.decode import decode_double
from maeyomi.double.solve import MAX_VALUE as DOUBLE_MAX
from maeyomi.double.solve import solve_double
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME, strongest_card
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, CardResult, GeneratedCard
from maeyomi.models.read_type import ReadType
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
NOT_READ: Final = "Datach Dragon Ball Z does not read {fields}"


@dataclass(frozen=True, slots=True)
class DeviceForm:
    """Which parts of the card maker a device reads, and how far each number goes."""

    fields: tuple[str, ...]
    hp_max: int
    st_max: int
    df_max: int
    steps: tuple[int, int, int] = (HUNDREDS, HUNDREDS, HUNDREDS)
    stat_keys: tuple[str, ...] = tuple(CLASSIC_STATS)


@dataclass(frozen=True, slots=True)
class DeviceChoice:
    """The options beside the shared request: a back read, a nearest match, a game's pick."""

    back_read: bool = False
    nearest: bool = False
    character: str | None = None
    level: int | None = None


@dataclass(frozen=True, slots=True)
class DeviceOutcome:
    """A built card, or every reason none could be built."""

    card: CardResult | None = None
    blockers: tuple[str, ...] = ()
    exact: bool = True


FORMS: Final[dict[Device, DeviceForm]] = {
    Device.BB2: DeviceForm(
        ("race", "class", "ability", "speed", "job", "backRead", "nearest"),
        SECOND_MAX_HP,
        SECOND_MAX_STAT,
        SECOND_MAX_STAT,
    ),
    Device.BB1: DeviceForm(
        ("race", "job", "backRead"), FIRST_MAX_HP, FIRST_MAX_STAT, FIRST_MAX_STAT
    ),
    Device.DOUBLE: DeviceForm(("job",), DOUBLE_MAX, DOUBLE_MAX, DOUBLE_MAX),
    Device.DATACH_DBZ: DeviceForm(
        ("dbz", "nearest"),
        MAX_HP,
        MAX_HALVED,
        MAX_HALVED,
        (HP_STEP, HALVED_STEP, HALVED_STEP),
        ("stat.hp", "stat.bp", "stat.dp"),
    ),
}


def device_named(key: str) -> Device:
    """The device a key names, or a ValueError listing the keys there are."""
    try:
        return Device(key.strip().lower())
    except ValueError as error:
        known = ", ".join(device.value for device in Device)
        message = f"unknown device {key!r}; known devices: {known}"
        raise ValueError(message) from error


def device_views() -> list[DeviceView]:
    """Every device, in the order the enum lists them, with its form."""
    return [
        DeviceView(
            key=device.value,
            english=device.english,
            japanese=device.japanese,
            fields=list(FORMS[device].fields),
            hp_max=FORMS[device].hp_max,
            st_max=FORMS[device].st_max,
            df_max=FORMS[device].df_max,
            steps=list(FORMS[device].steps),
            stat_keys=list(FORMS[device].stat_keys),
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


def read_as(device: Device, barcode: str) -> CardResult:
    """Decode a barcode the way the device reads it, raising BarcodeError on a refusal."""
    return printable_as(device, barcode, "").character


def printable_as(device: Device, barcode: str, name: str) -> AnyCard:
    """A card ready to print, its barcode decoded the way the device reads it."""
    if device is Device.BB1:
        first = decode_first(barcode)
        return GeneratedCard(name=name, barcode=first.barcode, character=first)
    if device is Device.DOUBLE:
        double = decode_double(barcode)
        return GeneratedCard(name=name, barcode=double.barcode, character=double)
    if device is Device.DATACH_DBZ:
        dbz = decode_dbz(barcode)
        return GeneratedCard(name=name, barcode=dbz.barcode, character=dbz)
    second = decode(barcode)
    return GeneratedCard(name=name, barcode=second.barcode, character=second)


def build_as(device: Device, request: CardRequest, choice: DeviceChoice) -> DeviceOutcome:
    """Build one card for a device other than the Barcode Battler II."""
    back_read = choice.back_read
    if device is Device.DATACH_DBZ:
        return _build_dbz(request, choice)
    if device is Device.DOUBLE:
        if back_read:
            return DeviceOutcome(blockers=(NO_BACK_READ,))
        outcome = solve_double(request)
        return DeviceOutcome(outcome.card, outcome.blockers)
    reading = ReadType.BACK if back_read else ReadType.FRONT
    first = solve_first(request, read_type=reading)
    return DeviceOutcome(first.card, first.blockers)


def cheat_as(device: Device, name: str | None) -> AnyCard:
    """The strongest card the device will read, under the typed name or the default one."""
    chosen = name or DEFAULT_CHEAT_NAME
    if device is Device.BB1:
        return strongest_first_card(chosen)
    if device is Device.DOUBLE:
        return strongest_double_card(chosen)
    if device is Device.DATACH_DBZ:
        return strongest_dbz_card(chosen)
    return strongest_card(chosen)


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


def _build_dbz(request: CardRequest, choice: DeviceChoice) -> DeviceOutcome:
    """Refuse what the game cannot read, then solve what it can, nearest when asked."""
    unread = unread_fields(request, back_read=choice.back_read)
    if unread:
        return DeviceOutcome(blockers=(NOT_READ.format(fields=", ".join(unread)),))
    name = choice.character
    try:
        character = None if name is None or not name.strip() else character_id(name)
    except ValueError as error:
        return DeviceOutcome(blockers=(str(error),))
    wanted = request_from(request, character=character, level=choice.level)
    outcome = solve_dbz_nearest(wanted) if choice.nearest else solve_dbz(wanted)
    return DeviceOutcome(outcome.card, outcome.blockers, exact=outcome.exact)


def _fact(label: Bilingual, value: Bilingual) -> FactView:
    """One line of facts in both languages."""
    return FactView(
        label=label.english, label_ja=label.japanese, value=value.english, value_ja=value.japanese
    )
