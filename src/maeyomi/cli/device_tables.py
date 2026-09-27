"""The tables and listings the command line prints, for whichever device was chosen.

`kinds`, `abilities`, `products` and `official` each describe what a device
does with a barcode, and the answer differs per device: the first Barcode
Battler's two-digit code is a flag rather than a power, the Double has its own
power table, and Datach Dragon Ball Z has fighters and items instead of races.
"""

from collections.abc import Sequence
from typing import Final

from maeyomi.bb1.flags import MAX_CODE as FLAG_MAX
from maeyomi.bb1.flags import MIN_CODE as FLAG_MIN
from maeyomi.bb1.flags import Flag
from maeyomi.datach.dbz_names import FIGHTERS, ITEMS
from maeyomi.double.abilities import DoubleAbility
from maeyomi.models.device import Device
from maeyomi.models.race import Race
from maeyomi.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from maeyomi.official.catalogue import (
    OfficialSet,
    device_cards,
    official_cards,
    rejected_transcriptions,
)
from maeyomi.products.japan import JapaneseProduct
from maeyomi.registry import readable_as, speed_note
from maeyomi.rendering.face import summary_of
from maeyomi.rendering.labels import RACE_DESCRIPTIONS, UNREADABLE, race_label

SEVEN_READ_NOTE: Final = (
    "   A 7-read card has no race any source records; it prints as kind unknown."
)


def kind_lines(device: Device) -> list[str]:
    """Every kind of card the device knows, in both languages."""
    if device is Device.DATACH_DBZ:
        fighters = [f"{key:3d}  {en} / {ja}" for key, (en, ja) in FIGHTERS.items()]
        items = [f"{key:3d}  {item.english} / {item.japanese}" for key, item in ITEMS.items()]
        return ["Fighters", *fighters, "Items", *items]
    lines: list[str] = []
    for race in Race:
        label = race_label(race)
        lines.append(f"{race.value}  {race.name.lower():18s} {label.english} / {label.japanese}")
        if device is Device.BB2:
            lines.append(f"   {RACE_DESCRIPTIONS[race]}")
    return [*lines, SEVEN_READ_NOTE] if device is Device.DOUBLE else lines


def ability_lines(device: Device) -> list[str]:
    """The device's own table for the two-digit code, or the game's item effects."""
    if device is Device.DATACH_DBZ:
        return [f"{key:02d}  {item.english}: {item.effect}" for key, item in ITEMS.items()]
    if device is Device.BB1:
        flags = (Flag.from_code(code) for code in range(FLAG_MIN, FLAG_MAX + 1))
        return [f"{flag.code:02d}  {flag.description}" for flag in flags]
    if device is Device.DOUBLE:
        powers = (DoubleAbility.from_code(code) for code in range(MIN_CODE, MAX_CODE + 1))
        return [f"{power.code:02d}  {power.description}" for power in powers]
    specials = (SpecialAbility.from_code(code) for code in range(MIN_CODE, MAX_CODE + 1))
    return [f"{special.code:02d}  {special.description}" for special in specials]


def product_lines(products: Sequence[JapaneseProduct], device: Device) -> list[str]:
    """One line per product: what the device makes of it, and its numbers."""
    lines = [
        f"{product.barcode}  {product.name}  {_shelf_text(product, device)}" for product in products
    ]
    return [*lines, f"{len(products)} product(s)"]


def _shelf_text(product: JapaneseProduct, device: Device) -> str:
    """What the device makes of a product, or that its reader cannot read it."""
    card = readable_as(device, product.barcode)
    if card is None:
        return UNREADABLE.english
    summary = summary_of(card)
    note = speed_note(device, product.barcode)
    text = f"{summary.label.english}  {summary.stats.english}"
    return text if note is None else f"{text}; {note.english}"


def official_sets(device: Device | None) -> tuple[OfficialSet, ...]:
    """The sets of one device, or every set when no device was named."""
    return tuple(entry for entry in OfficialSet if device is None or entry.device is device)


def official_lines(device: Device | None) -> list[str]:
    """Each set with its printable count, the total, and the transcriptions left out."""
    sets = official_sets(device)
    rows = [
        f"{len(official_cards(entry)):4d}  {entry.name.lower():24s}  {entry.english}, "
        f"read by the {entry.device.english}"
        for entry in sets
    ]
    total = len(official_cards()) if device is None else len(device_cards(device))
    skipped = [
        f"skipped {entry.barcode} {entry.name}: its check digit is wrong"
        for entry in rejected_transcriptions()
        if entry.official_set in sets
    ]
    return [*rows, f"{total:4d}  total printable", *skipped]
