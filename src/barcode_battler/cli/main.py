"""Command line interface.

Three verbs. `random` fills a sheet from ranges, `generate` builds one card to
an exact specification, and `decode` reads a barcode back so a card can be
checked by hand. `abilities` prints the published ability table, because the
device has numeric ability codes rather than named elements.
"""

from pathlib import Path
from typing import Annotated

import typer

from barcode_battler.cli.parsing import parse_character_class, parse_constraint, parse_race
from barcode_battler.cli.report import DISCLAIMER, comparison_lines, shortfall_lines
from barcode_battler.decoder.decode import decode as decode_barcode
from barcode_battler.decoder.errors import BarcodeError
from barcode_battler.generator.random_cards import generate_random
from barcode_battler.generator.solve import solve
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from barcode_battler.rendering.export import ImageFormat, export_images
from barcode_battler.rendering.sheet import write_sheet

app = typer.Typer(
    add_completion=False,
    help="Generate printable cards for the Barcode Battler II.",
    no_args_is_help=True,
)

HpOption = Annotated[str | None, typer.Option("--hp", help="Exact value, range or bound.")]
StOption = Annotated[
    str | None, typer.Option("--st", "--attack", help="Exact value, range or bound.")
]
DfOption = Annotated[
    str | None, typer.Option("--df", "--defense", help="Exact value, range or bound.")
]
RaceOption = Annotated[str | None, typer.Option("--race", help="Race or item type by name.")]
ClassOption = Annotated[str | None, typer.Option("--class", help="warrior or magician.")]
JobOption = Annotated[int | None, typer.Option("--job", min=0, max=9, help="Job digit 0-9.")]
SpeedOption = Annotated[int | None, typer.Option("--speed", min=0, max=9, help="Speed digit.")]
AbilityOption = Annotated[
    int | None, typer.Option("--ability", min=MIN_CODE, max=MAX_CODE, help="Ability code.")
]
OutputOption = Annotated[Path, typer.Option("--output", "-o", help="PDF to write.")]
ImagesOption = Annotated[
    ImageFormat | None, typer.Option("--images", help="Also export page images.")
]


@app.command()
def random(
    output: OutputOption,
    count: Annotated[int, typer.Option("--count", "-n", min=1)] = 9,
    hp: HpOption = None,
    st: StOption = None,
    df: DfOption = None,
    race: RaceOption = None,
    character_class: ClassOption = None,
    job: JobOption = None,
    speed: SpeedOption = None,
    ability: AbilityOption = None,
    seed: Annotated[int | None, typer.Option("--seed", help="Repeat an earlier run.")] = None,
    images: ImagesOption = None,
) -> None:
    """Fill a sheet with random cards drawn through the real algorithm."""
    template = _request(
        "",
        hp,
        st,
        df,
        race=race,
        character_class=character_class,
        job=job,
        speed=speed,
        ability=ability,
    )
    batch = generate_random(count, template=template, seed=seed)
    if batch.shortfall:
        for line in shortfall_lines(len(batch.cards), batch.requested, batch.reason):
            typer.echo(line, err=True)
        raise typer.Exit(code=1)
    _write(batch.cards, output, images)


@app.command()
def generate(
    output: OutputOption,
    name: Annotated[str, typer.Option("--name", help="Printed on the card only.")] = "Card",
    hp: HpOption = None,
    st: StOption = None,
    df: DfOption = None,
    race: RaceOption = None,
    character_class: ClassOption = None,
    job: JobOption = None,
    speed: SpeedOption = None,
    ability: AbilityOption = None,
    images: ImagesOption = None,
) -> None:
    """Build one card whose barcode decodes to exactly the requested attributes."""
    request = _request(
        name,
        hp,
        st,
        df,
        race=race,
        character_class=character_class,
        job=job,
        speed=speed,
        ability=ability,
    )
    outcome = solve(request)
    if outcome.barcode is None or outcome.character is None:
        for reason in outcome.blockers:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    for line in comparison_lines(request, outcome.character):
        typer.echo(line)
    typer.echo("")
    card = GeneratedCard(name=name, barcode=outcome.barcode, character=outcome.character)
    _write((card,), output, images)


@app.command()
def decode(barcode: Annotated[str, typer.Argument(help="8 or 13 digit code.")]) -> None:
    """Read a barcode the way the device reads it."""
    try:
        character = decode_barcode(barcode)
    except BarcodeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    character_class = character.character_class
    typer.echo(f"Barcode   {character.barcode}")
    typer.echo(f"Read      {character.read_type.value}")
    typer.echo(f"HP        {character.hp}")
    typer.echo(f"ST        {character.st}")
    typer.echo(f"DF        {character.df}")
    typer.echo(f"Race      {character.race.name.replace('_', ' ').title()}")
    typer.echo(f"Class     {character_class.value.title() if character_class else 'Item'}")
    typer.echo(f"Job       {character.job}")
    typer.echo(f"Speed     {character.speed if character.speed is not None else '-'}")
    typer.echo(f"Ability   {character.special.code:02d} {character.special.description}")


@app.command()
def abilities() -> None:
    """Print the published special ability table."""
    for code in range(MIN_CODE, MAX_CODE + 1):
        ability = SpecialAbility.from_code(code)
        typer.echo(f"{ability.code:02d}  {ability.description}")


def _request(
    name: str,
    hp: str | None,
    st: str | None,
    df: str | None,
    *,
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
            race=parse_race(race),
            character_class=parse_character_class(character_class),
            job=job,
            speed=speed,
            special=ability,
        )
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error


def _write(cards: tuple[GeneratedCard, ...], output: Path, images: ImageFormat | None) -> None:
    """Write the sheet, export images when asked, and state what was verified."""
    pages = write_sheet(cards, output)
    typer.echo(f"Wrote {len(cards)} card(s) across {pages} page(s) to {output}")
    if images is not None:
        directory = output.with_name(f"{output.stem}-images")
        written = export_images(output, directory, image_format=images)
        typer.echo(f"Wrote {len(written)} image(s) to {directory}")
    typer.echo(DISCLAIMER)
