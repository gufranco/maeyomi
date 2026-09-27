"""The commands, run against the first Barcode Battler rather than the second.

`main` hands over here when `--device bb1` is given, so each command keeps one
entry point and this module holds what the first device reads differently.
"""

from pathlib import Path

import typer

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.cheat import strongest_first_card, strongest_first_items
from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.solve import solve_first
from maeyomi.cli.common import sheet_layout, write_cards
from maeyomi.cli.report import comparison_table
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.read_type import ReadType
from maeyomi.rendering.export import ImageFormat
from maeyomi.rendering.face import face_of
from maeyomi.rendering.stat_tiles import StatTile

UNKNOWN = "unknown"


def show_first(
    barcode: str, *, output: Path | None, name: str, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print what the first device reads, and the card when asked."""
    try:
        card = decode_first(barcode)
    except BarcodeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    for line in describe_first(card):
        typer.echo(line)
    if output is not None:
        printable = GeneratedCard(name=name, barcode=card.barcode, character=card)
        write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def describe_first(card: FirstBattlerCard) -> list[str]:
    """One line per field, with what no source records said plainly."""
    return [
        f"Device    {Device.BB1.english}",
        f"Barcode   {card.barcode}",
        f"Read      {card.read_type.value}",
        f"HP        {card.hp}",
        f"ST        {card.st}",
        f"DF        {card.df}",
        f"Race      {_race(card)}",
        f"Job       {card.job}",
        f"DX        {UNKNOWN if card.dx is None else card.dx}",
        f"Flag      {card.flag.code:02d} {card.flag.description}",
    ]


def generate_first(
    request: CardRequest,
    *,
    back_read: bool,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Build one first-device card to order, or say which field blocks it."""
    reading = ReadType.BACK if back_read else ReadType.FRONT
    outcome = solve_first(request, read_type=reading)
    if outcome.card is None:
        for reason in outcome.blockers:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    for line in _comparison(request, outcome.card):
        typer.echo(line)
    typer.echo("")
    printable = GeneratedCard(
        name=request.name, barcode=outcome.card.barcode, character=outcome.card
    )
    write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def cheat_first(
    name: str, *, items: bool, output: Path, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print the strongest first-device fighter, and its items when asked."""
    fighter = strongest_first_card(name)
    card = fighter.character
    typer.echo(f"{fighter.name}: HP {card.hp}, ST {card.st}, DF {card.df}")
    typer.echo(f"Flag {card.flag.code:02d} {card.flag.description}")
    extras = strongest_first_items() if items else ()
    for extra in extras:
        typer.echo(_item_line(extra.name, extra.character))
    write_cards((fighter, *extras), output, images, sheet_layout(print_shop=print_shop))


def _item_line(name: str, card: FirstBattlerCard) -> str:
    """One line naming an item, what it carries, and its flag."""
    tiles: tuple[StatTile, ...] = face_of(card).tiles
    carried = ", ".join(f"{tile.key} {tile.value}" for tile in tiles)
    return f"{name}: {carried}; flag {card.flag.code:02d} {card.flag.description}"


def _comparison(request: CardRequest, card: FirstBattlerCard) -> list[str]:
    """Requested beside generated, for every field the first device reads."""
    return comparison_table(
        [
            ("HP", str(request.hp), str(card.hp)),
            ("ST", str(request.st), str(card.st)),
            ("DF", str(request.df), str(card.df)),
            ("Race", _requested_race(request), _race(card)),
            ("Job", _optional(request.job), str(card.job)),
            ("DX", _optional(request.speed), _optional(card.dx)),
            ("Flag", _optional(request.special), f"{card.flag.code:02d}"),
        ]
    )


def _race(card: FirstBattlerCard) -> str:
    """The race's name, or unknown for an enemy read from the back."""
    return UNKNOWN if card.race is None else card.race.name.replace("_", " ").title()


def _requested_race(request: CardRequest) -> str:
    """The requested race's name, or a dash."""
    return "-" if request.race is None else request.race.name.replace("_", " ").title()


def _optional(value: int | None) -> str:
    """A value, or a dash when absent."""
    return "-" if value is None else str(value)
