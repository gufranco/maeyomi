"""The commands, run against the Barcode Battler II Double.

`main` hands over here when `--device double` is given. The Double reads the
II's codes the II's way, so what this module adds is its own 7-read, its class
names and its power table.
"""

from pathlib import Path

import typer

from maeyomi.cli.common import sheet_layout, write_cards
from maeyomi.cli.report import comparison_table
from maeyomi.decoder.errors import BarcodeError
from maeyomi.double.card import DoubleCard
from maeyomi.double.cheat import strongest_double_card, strongest_double_items
from maeyomi.double.decode import decode_double
from maeyomi.double.solve import solve_double
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.rendering.export import ImageFormat
from maeyomi.rendering.face import face_of
from maeyomi.rendering.labels import double_class_label

UNKNOWN = "unknown"
NO_BACK_READ = (
    "the Double reads II back-read codes the II's way; build them with --device bb2, "
    "and use --device double for its own 7-read"
)


def show_double(
    barcode: str, *, output: Path | None, name: str, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print what the Double reads, and the card when asked."""
    try:
        card = decode_double(barcode)
    except BarcodeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    for line in describe_double(card):
        typer.echo(line)
    if output is not None:
        printable = GeneratedCard(name=name, barcode=card.barcode, character=card)
        write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def describe_double(card: DoubleCard) -> list[str]:
    """One line per field, with what no source records said plainly."""
    return [
        f"Device    {Device.DOUBLE.english}",
        f"Barcode   {card.barcode}",
        f"Read      {card.reading.value}",
        f"HP        {card.hp}",
        f"ST        {card.st}",
        f"DF        {card.df}",
        f"Race      {_race(card)}",
        f"Class     {double_class_label(card.job).english}",
        f"Job       {card.job}",
        f"Speed     {UNKNOWN if card.speed is None else card.speed}",
        f"Power     {card.special.code:02d} {card.special.description}",
    ]


def generate_double(
    request: CardRequest,
    *,
    back_read: bool,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Build one 7-read card to order, or say which field blocks it."""
    if back_read:
        typer.echo(NO_BACK_READ, err=True)
        raise typer.Exit(code=2)
    outcome = solve_double(request)
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


def cheat_double(
    name: str, *, items: bool, output: Path, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print the strongest Double fighter, and its items when asked."""
    fighter = strongest_double_card(name)
    card = fighter.character
    typer.echo(f"{fighter.name}: HP {card.hp}, ST {card.st}, DF {card.df}")
    typer.echo(f"Power {card.special.code:02d} {card.special.description}")
    extras = strongest_double_items() if items else ()
    for extra in extras:
        typer.echo(_item_line(extra.name, extra.character))
    write_cards((fighter, *extras), output, images, sheet_layout(print_shop=print_shop))


def _item_line(name: str, card: DoubleCard) -> str:
    """One line naming an item, what it carries, and its power."""
    carried = ", ".join(f"{tile.key} {tile.value}" for tile in face_of(card).tiles)
    return f"{name}: {carried}; power {card.special.code:02d} {card.special.description}"


def _comparison(request: CardRequest, card: DoubleCard) -> list[str]:
    """Requested beside generated, for every field the 7-read carries."""
    return comparison_table(
        [
            ("HP", str(request.hp), str(card.hp)),
            ("ST", str(request.st), str(card.st)),
            ("DF", str(request.df), str(card.df)),
            ("Job", "-" if request.job is None else str(request.job), str(card.job)),
            (
                "Power",
                "-" if request.special is None else str(request.special),
                f"{card.special.code:02d}",
            ),
        ]
    )


def _race(card: DoubleCard) -> str:
    """The race's name, or unknown for a 7-read card."""
    return UNKNOWN if card.race is None else card.race.name.replace("_", " ").title()
