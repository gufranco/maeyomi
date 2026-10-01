"""Read, build and cheat on any device or game through one entry point.

Every surface that lets a person choose a device, the web page and the command
line alike, calls these rather than branching on the device itself, so a
feature added for one device cannot quietly stay Barcode Battler II only.

Every device reads any valid EAN-8 or EAN-13, and every one refuses the same
malformed codes, but each turns a code into a different card: the same digits
are a robot on the Barcode Battler II and Goku in Datach Dragon Ball Z.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from maeyomi.barcode.geometry import Symbology, symbology_of
from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.solve import solve_first
from maeyomi.cheat_kinds import cheat_kind
from maeyomi.datach.dbz import decode_dbz
from maeyomi.datach.dbz_names import character_id
from maeyomi.datach.dbz_reader import Readability, ReaderRefusalError, readability
from maeyomi.datach.dbz_solve import request_from, solve_dbz, solve_dbz_nearest, unread_fields
from maeyomi.datach.game_reader import game_readability
from maeyomi.datach.game_types import DatachGame, GameOrder
from maeyomi.datach.games import game_for
from maeyomi.decoder.decode import decode
from maeyomi.double.decode import decode_double
from maeyomi.double.solve import solve_double
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, CardResult, GeneratedCard
from maeyomi.models.read_type import ReadType
from maeyomi.rendering.labels import SPEED_DEPENDENT, Bilingual
from maeyomi.said import Said, fields_in_japanese, said_of

NO_DOUBLE_BACK_READ: Final = Said(
    "the Double reads II back-read codes the II's way; build them with --device bb2, "
    "and use --device double for its own 7-read",
    "ダブルは II の うしろよみの コードを II と おなじに よむので、バーコードバトラーII で"
    " つくって。ダブルの 7よみは ダブルで つくれる",
)


def not_read(device: Device, fields: Sequence[str]) -> Said:
    """Why a device refuses a request naming fields it has no place for."""
    return Said(
        f"{device.english} does not read {', '.join(fields)}",
        f"{device.japanese} は {fields_in_japanese(fields)} を よまない",
    )


def no_game_card(device: Device) -> Said:
    """Why a game refuses a card that none of its codes gives."""
    return Said(
        f"{device.english} reads no card like the one asked for",
        f"{device.japanese} には その カードは ない",
    )


@dataclass(frozen=True, slots=True)
class DeviceChoice:
    """The options beside the shared request: a back read, a nearest match, a game's pick."""

    back_read: bool = False
    nearest: bool = False
    character: str | None = None
    level: int | None = None
    picks: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True, slots=True)
class DeviceOutcome:
    """A built card, or every reason none could be built."""

    card: CardResult | None = None
    blockers: tuple[str, ...] = ()
    exact: bool = True
    companion: CardResult | None = None


def device_named(key: str) -> Device:
    """The device a key names, or a ValueError listing the keys there are."""
    try:
        return Device(key.strip().lower())
    except ValueError as error:
        known = ", ".join(device.value for device in Device)
        message = Said(
            f"unknown device {key!r}; known devices: {known}",
            f"{key!r} という マシンや ゲームは ない。つかえるのは {known}",
        )
        raise ValueError(message) from error


def read_as(device: Device, barcode: str) -> CardResult:
    """Decode a barcode the way the device reads it, raising BarcodeError on a refusal."""
    return printable_as(device, barcode, "").character


def readable_as(device: Device, barcode: str) -> CardResult | None:
    """The card a printed EAN symbol makes, or None when the device's reader can never read it."""
    if symbology_of(device) is not Symbology.EAN:
        return None
    try:
        return read_as(device, barcode)
    except ReaderRefusalError:
        return None


def speed_note(device: Device, barcode: str) -> Bilingual | None:
    """A caution when the device reads the code only at some swipe speeds."""
    if device is Device.DATACH_DBZ and readability(barcode) is Readability.SPEED_DEPENDENT:
        return SPEED_DEPENDENT
    game = game_for(device)
    datach = game is not None and game.datach_reader
    if datach and game_readability(barcode) is Readability.SPEED_DEPENDENT:
        return SPEED_DEPENDENT
    return None


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
    game = game_for(device)
    if game is not None:
        read = game.decode(barcode)
        return GeneratedCard(name=name, barcode=read.barcode, character=read)
    second = decode(barcode)
    return GeneratedCard(name=name, barcode=second.barcode, character=second)


def build_as(device: Device, request: CardRequest, choice: DeviceChoice) -> DeviceOutcome:
    """Build one card to order for the device, or say why none exists."""
    reading = ReadType.BACK if choice.back_read else ReadType.FRONT
    if device is Device.DATACH_DBZ:
        return _build_dbz(request, choice)
    game = game_for(device)
    if game is not None:
        return _build_game(device, game, request, choice)
    if device is Device.DOUBLE:
        if choice.back_read:
            return DeviceOutcome(blockers=(NO_DOUBLE_BACK_READ,))
        double = solve_double(request)
        return DeviceOutcome(double.card, double.blockers)
    if device is Device.BB1:
        first = solve_first(request, read_type=reading)
        return DeviceOutcome(first.card, first.blockers)
    second = solve(request, read_type=reading)
    return DeviceOutcome(second.character, second.blockers)


def cheat_as(device: Device, name: str | None) -> AnyCard:
    """The device's default cheat card, under the typed name or the default one."""
    return cheat_kind(device, None).cards(name or DEFAULT_CHEAT_NAME)[0]


def _build_dbz(request: CardRequest, choice: DeviceChoice) -> DeviceOutcome:
    """Refuse what the game cannot read, then solve what it can, nearest when asked."""
    unread = unread_fields(request, back_read=choice.back_read)
    if unread:
        return DeviceOutcome(blockers=(not_read(Device.DATACH_DBZ, unread),))
    name = choice.character
    try:
        character = None if name is None or not name.strip() else character_id(name)
    except ValueError as error:
        return DeviceOutcome(blockers=(said_of(error),))
    wanted = request_from(request, character=character, level=choice.level)
    outcome = solve_dbz_nearest(wanted) if choice.nearest else solve_dbz(wanted)
    return DeviceOutcome(outcome.card, outcome.blockers, exact=outcome.exact)


def _build_game(
    device: Device, game: DatachGame, request: CardRequest, choice: DeviceChoice
) -> DeviceOutcome:
    """Refuse what the game cannot read, then build the card from its own tables."""
    unread = unread_fields(request, back_read=choice.back_read)
    if unread:
        return DeviceOutcome(blockers=(not_read(device, unread),))
    name = choice.character
    try:
        ident = None if name is None or not name.strip() else game.named(name)
    except ValueError as error:
        return DeviceOutcome(blockers=(said_of(error),))
    stats = (request.hp, request.st, request.df)
    order = GameOrder(ident, stats, choice.picks)
    card = game.build(order)
    if card is None:
        return DeviceOutcome(blockers=(no_game_card(device),))
    exact = all(
        constraint.admits(card.value(key))
        for key, constraint in zip(game.stat_keys, stats, strict=False)
        if any(stat.key == key for stat in card.stats)
    )
    return DeviceOutcome(card, exact=exact, companion=game.companion(order))


def cheat_companion_as(device: Device, name: str | None) -> AnyCard | None:
    """The default cheat card's partner, for a game that reads its cards in pairs."""
    cards = cheat_kind(device, None).cards(name or DEFAULT_CHEAT_NAME)
    game = game_for(device)
    paired = game is not None and game.strongest_companion() is not None
    return cards[1] if paired and len(cards) > 1 else None
