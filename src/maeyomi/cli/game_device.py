"""The commands, run against the Datach games after Dragon Ball Z.

`main` hands over here for any game in `datach.games`. Each game reads its
own numbers, so the shared options map onto them in the order the game prints
them: `--hp` is the first, `--st` the second and `--df` the third. The card is
picked with `--character`, by the game's own name or its number.
"""

from pathlib import Path

import typer

from maeyomi.cli.common import sheet_layout, write_cards
from maeyomi.datach.dbz_solve import unread_fields
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import CardResult
from maeyomi.registry import (
    GAME_NOT_READ,
    DeviceChoice,
    build_as,
    cheat_as,
    printable_as,
    read_as,
    speed_note,
)
from maeyomi.rendering.export import ImageFormat
from maeyomi.rendering.face import face_of
from maeyomi.rendering.labels import STAT_LABELS


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
    return [*head, *numbers, f"{heading:<10}{face.power_text.english}"]


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
        typer.echo(GAME_NOT_READ.format(game=device.english, fields=", ".join(unread)), err=True)
        raise typer.Exit(code=2)
    outcome = build_as(device, request, choice)
    if outcome.card is None:
        for reason in outcome.blockers:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    for line in describe_game(device, outcome.card):
        typer.echo(line)
    typer.echo("")
    printable = printable_as(device, outcome.card.barcode, request.name)
    write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


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
    card = cheat_as(device, name)
    read = card.character
    numbers = ", ".join(
        f"{STAT_LABELS[tile.key].english} {tile.value}" for tile in face_of(read).tiles
    )
    kind = face_of(read).kind.english
    typer.echo(f"{card.name}: {kind}" + (f", {numbers}" if numbers else ""))
    write_cards((card,), output, images, sheet_layout(print_shop=print_shop))
