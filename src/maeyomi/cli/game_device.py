"""The commands, run against the Datach games after Dragon Ball Z.

`main` hands over here for any game in `datach.games`. Each game reads its
own numbers, so the shared options map onto them in the order the game prints
them: `--hp` is the first, `--st` the second and `--df` the third. The card is
picked with `--character`, by the game's own name or its number.
"""

from pathlib import Path
from typing import Final

import typer

from maeyomi.cheat_kinds import cheat_kind, cheat_kinds
from maeyomi.cli.common import sheet_layout, write_cards
from maeyomi.datach.dbz_solve import unread_fields
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import CardResult
from maeyomi.registry import (
    DeviceChoice,
    build_as,
    cheat_as,
    cheat_companion_as,
    not_read,
    printable_as,
    read_as,
    speed_note,
)
from maeyomi.rendering.export import ImageFormat
from maeyomi.rendering.face import face_of
from maeyomi.rendering.labels import STAT_LABELS

BAD_PICK: Final = "--pick takes key=value with a whole number, such as sr=1; got {pick!r}"
ONLY_GAME_PICKS: Final = "only a Datach game after Dragon Ball Z reads --pick"
CLOSEST: Final = "no card has exactly those numbers; offering the closest one that prints"


def parse_picks(picks: list[str]) -> tuple[tuple[str, int], ...]:
    """Each key=value choice, or a usage error naming the one that is malformed."""
    parsed: list[tuple[str, int]] = []
    for pick in picks:
        key, _, value = pick.partition("=")
        if not key.strip() or not value.strip().isdigit():
            typer.echo(BAD_PICK.format(pick=pick), err=True)
            raise typer.Exit(code=2)
        parsed = [*parsed, (key.strip(), int(value))]
    return tuple(parsed)


def refuse_picks(picks: list[str]) -> None:
    """Stop when --pick was given for a device that has no such choices."""
    if picks:
        typer.echo(ONLY_GAME_PICKS, err=True)
        raise typer.Exit(code=2)


def show_game(
    device: Device,
    barcode: str,
    *,
    output: Path | None,
    name: str,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Print what the game reads, and the card when asked."""
    try:
        card = read_as(device, barcode)
    except BarcodeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    for line in describe_game(device, card):
        typer.echo(line)
    note = speed_note(device, card.barcode)
    if note is not None:
        typer.echo(f"Note      {note.english}")
    if output is not None:
        printable = printable_as(device, card.barcode, name)
        write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def describe_game(device: Device, card: CardResult) -> list[str]:
    """One line per field the game shows, taken from the face it prints."""
    face = face_of(card)
    head = [
        f"Device    {device.english}",
        f"Barcode   {card.barcode}",
        f"Kind      {face.detail.english}",
        f"Name      {face.kind.english} / {face.kind.japanese}",
    ]
    numbers = [f"{STAT_LABELS[tile.key].english:<10}{tile.value}" for tile in face.tiles]
    heading = face.power_heading.english if face.power_heading else ""
    return [*head, *numbers, f"{heading:<9} {face.power_text.english}"]


def generate_game(
    device: Device,
    request: CardRequest,
    choice: DeviceChoice,
    *,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Build one card to order, or say what blocks it."""
    unread = unread_fields(request, back_read=choice.back_read)
    if unread:
        typer.echo(not_read(device, unread), err=True)
        raise typer.Exit(code=2)
    outcome = build_as(device, request, choice)
    if outcome.card is None:
        for reason in outcome.blockers:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    if not outcome.exact:
        typer.echo(CLOSEST, err=True)
    for line in describe_game(device, outcome.card):
        typer.echo(line)
    typer.echo("")
    printable = printable_as(device, outcome.card.barcode, request.name)
    partner = outcome.companion
    cards = (
        (printable,)
        if partner is None
        else (printable, printable_as(device, partner.barcode, request.name))
    )
    write_cards(cards, output, images, sheet_layout(print_shop=print_shop))


def cheat_game(
    device: Device,
    name: str,
    *,
    items: bool,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Print the game's strongest card, and its strongest items when the game has them."""
    if items:
        typer.echo(f"{device.english} has no strongest items; printing the card alone", err=True)
    try:
        card = cheat_as(device, name)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    read = card.character
    numbers = ", ".join(
        f"{STAT_LABELS[tile.key].english} {tile.value}" for tile in face_of(read).tiles
    )
    kind = face_of(read).kind.english
    typer.echo(f"{card.name}: {kind}" + (f", {numbers}" if numbers else ""))
    partner = cheat_companion_as(device, name)
    cards = (card,) if partner is None else (card, partner)
    write_cards(cards, output, images, sheet_layout(print_shop=print_shop))


def cheat_kind_lines(device: Device) -> list[str]:
    """Every cheat kind the device offers, its key first, the default at the top."""
    return [f"{kind.key}: {kind.english}" for kind in cheat_kinds(device)]


def cheat_of_kind(
    device: Device,
    key: str,
    name: str,
    *,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Print every card of one cheat kind, a line for each, or say why the kind does not exist."""
    try:
        cards = cheat_kind(device, key).cards(name)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    for card in cards:
        face = face_of(card.character)
        numbers = ", ".join(f"{STAT_LABELS[tile.key].english} {tile.value}" for tile in face.tiles)
        said = f"{face.kind.english}" + (f", {numbers}" if numbers else "")
        typer.echo(f"{card.barcode} {said}; {face.power_text.english}")
    write_cards(cards, output, images, sheet_layout(print_shop=print_shop))
