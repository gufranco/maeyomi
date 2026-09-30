"""Pieces every command shares: reading the options into a request, and writing a sheet."""

from pathlib import Path

import typer

from maeyomi.cli.parsing import parse_character_class, parse_constraint, parse_race
from maeyomi.cli.report import disclaimers
from maeyomi.models.card_request import CardRequest
from maeyomi.models.generated_card import AnyCard
from maeyomi.rendering.export import ImageFormat, export_images
from maeyomi.rendering.layout import SheetLayout
from maeyomi.rendering.sheet import write_sheet


def build_request(
    name: str,
    hp: str | None,
    st: str | None,
    df: str | None,
    *,
    herbs: str | None,
    magic: str | None,
    race: str | None,
    character_class: str | None,
    job: int | None,
    speed: int | None,
    ability: int | None,
) -> CardRequest:
    """Build a request from the options, reporting an unreadable one."""
    try:
        return CardRequest(
            name=name,
            hp=parse_constraint(hp),
            st=parse_constraint(st),
            df=parse_constraint(df),
            pp=parse_constraint(herbs),
            mp=parse_constraint(magic),
            race=parse_race(race),
            character_class=parse_character_class(character_class),
            job=job,
            speed=speed,
            special=ability,
        )
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error


def sheet_layout(*, print_shop: bool) -> SheetLayout:
    """The sheet the options ask for."""
    return SheetLayout.print_shop() if print_shop else SheetLayout()


def write_cards(
    cards: tuple[AnyCard, ...],
    output: Path,
    images: ImageFormat | None,
    layout: SheetLayout | None = None,
) -> None:
    """Write the sheet, export images when asked, and state what was verified."""
    pages = write_sheet(cards, output, layout=layout)
    typer.echo(f"Wrote {len(cards)} card(s) across {pages} page(s) to {output}")
    if images is not None:
        directory = output.with_name(f"{output.stem}-images")
        written = export_images(output, directory, image_format=images)
        typer.echo(f"Wrote {len(written)} image(s) to {directory}")
    for line in disclaimers(cards):
        typer.echo(line)
