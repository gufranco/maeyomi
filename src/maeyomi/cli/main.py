"""Command line interface.

`random` fills a sheet from ranges, `generate` builds one card to an exact
specification, `official` prints the cards Epoch released, `cheat` prints the
strongest card the device will read, and `decode` reads a barcode back so a card
can be checked by hand. `abilities` prints the published ability table, because the
device has numeric ability codes rather than named elements.
"""

import webbrowser
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from maeyomi.cli.common import build_request, sheet_layout, write_cards
from maeyomi.cli.doctor import State, machine, package, worst
from maeyomi.cli.double_device import cheat_double, generate_double, show_double
from maeyomi.cli.first_device import cheat_first, generate_first, show_first
from maeyomi.cli.report import DISCLAIMER, comparison_lines, fit_line, shortfall_lines
from maeyomi.decoder.decode import decode as decode_barcode
from maeyomi.decoder.errors import BarcodeError
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME, strongest_card
from maeyomi.generator.cheat_items import strongest_items
from maeyomi.generator.nearest import solve_nearest
from maeyomi.generator.random_cards import generate_random
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.device import Device
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from maeyomi.official.catalogue import (
    OfficialSet,
    official_cards,
    rejected_transcriptions,
)
from maeyomi.products.japan import product_cards, random_products, search_products
from maeyomi.rendering.export import ImageFormat
from maeyomi.rendering.labels import RACE_DESCRIPTIONS, race_label
from maeyomi.rendering.stat_tiles import stat_tiles

app = typer.Typer(
    add_completion=False,
    help="Generate printable cards for the Barcode Battler II.",
    no_args_is_help=True,
)

MARKS = {State.OK: "ok  ", State.WARN: "warn", State.FAIL: "FAIL"}
VERDICTS = {
    State.OK: "everything checked out",
    State.WARN: "everything checked out, with something worth knowing above",
    State.FAIL: "something is wrong, and a card printed now may not read",
}

HpOption = Annotated[str | None, typer.Option("--hp", help="Exact value, range or bound.")]
StOption = Annotated[
    str | None, typer.Option("--st", "--attack", help="Exact value, range or bound.")
]
DfOption = Annotated[
    str | None, typer.Option("--df", "--defense", help="Exact value, range or bound.")
]
HerbsOption = Annotated[
    str | None,
    typer.Option("--herbs", "--pp", help="Herbs a helper item gives, 0-99: exact, range or bound."),
]
MagicOption = Annotated[
    str | None,
    typer.Option("--magic", "--mp", help="Magic points a helper item gives, 0-99."),
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
PrintShopOption = Annotated[
    bool,
    typer.Option(
        "--print-shop",
        help="One card per page with a 3 mm bleed, as a commercial printer asks for.",
    ),
]
NearestOption = Annotated[
    bool, typer.Option("--nearest", help="On an impossible request, offer the closest card.")
]
DeviceOption = Annotated[
    Device,
    typer.Option(
        "--device",
        help=(
            "bb2 for the Barcode Battler II, bb1 for the first Barcode Battler, "
            "double for the Barcode Battler II Double."
        ),
    ),
]
BackReadOption = Annotated[
    bool, typer.Option("--back-read", help="Build a card the device reads from the back.")
]


@app.command()
def random(
    output: OutputOption,
    count: Annotated[int, typer.Option("--count", "-n", min=1)] = 9,
    hp: HpOption = None,
    st: StOption = None,
    df: DfOption = None,
    herbs: HerbsOption = None,
    magic: MagicOption = None,
    race: RaceOption = None,
    character_class: ClassOption = None,
    job: JobOption = None,
    speed: SpeedOption = None,
    ability: AbilityOption = None,
    seed: Annotated[int | None, typer.Option("--seed", help="Repeat an earlier run.")] = None,
    images: ImagesOption = None,
    print_shop: PrintShopOption = False,
) -> None:
    """Fill a sheet with random cards drawn through the real algorithm."""
    template = build_request(
        "",
        hp,
        st,
        df,
        herbs=herbs,
        magic=magic,
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
    write_cards(batch.cards, output, images, sheet_layout(print_shop=print_shop))


@app.command()
def generate(
    output: OutputOption,
    name: Annotated[str, typer.Option("--name", help="Printed on the card only.")] = "Card",
    hp: HpOption = None,
    st: StOption = None,
    df: DfOption = None,
    herbs: HerbsOption = None,
    magic: MagicOption = None,
    race: RaceOption = None,
    character_class: ClassOption = None,
    job: JobOption = None,
    speed: SpeedOption = None,
    ability: AbilityOption = None,
    images: ImagesOption = None,
    nearest: NearestOption = False,
    back_read: BackReadOption = False,
    device: DeviceOption = Device.BB2,
    print_shop: PrintShopOption = False,
) -> None:
    """Build one card whose barcode decodes to exactly the requested attributes."""
    request = build_request(
        name,
        hp,
        st,
        df,
        herbs=herbs,
        magic=magic,
        race=race,
        character_class=character_class,
        job=job,
        speed=speed,
        ability=ability,
    )
    if device is not Device.BB2:
        build = generate_first if device is Device.BB1 else generate_double
        build(request, back_read=back_read, output=output, images=images, print_shop=print_shop)
        return
    reading = ReadType.BACK if back_read else ReadType.FRONT
    outcome = solve(request, read_type=reading)
    if outcome.barcode is None or outcome.character is None:
        _report_blocked(request, outcome.blockers, nearest=nearest, back_read=back_read)
        character = _nearest_or_exit(request, outcome.blockers)
        barcode = character.barcode
    else:
        character = outcome.character
        barcode = outcome.barcode
    for line in comparison_lines(request, character):
        typer.echo(line)
    typer.echo("")
    write_cards(
        (GeneratedCard(name=name, barcode=barcode, character=character),),
        output,
        images,
        sheet_layout(print_shop=print_shop),
    )


def _report_blocked(
    request: CardRequest, reasons: tuple[str, ...], *, nearest: bool, back_read: bool
) -> None:
    """Print why the exact request failed, and stop unless a nearest match was asked for."""
    for reason in reasons:
        typer.echo(reason, err=True)
    if not nearest:
        raise typer.Exit(code=1)
    if back_read:
        typer.echo("--nearest covers front reads only", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"no exact match for {request.name or 'this card'}; offering the closest", err=True)


def _nearest_or_exit(request: CardRequest, reasons: tuple[str, ...]) -> BarcodeBattlerCharacter:
    """Return the closest reachable card, or exit reporting why there is none."""
    near = solve_nearest(request)
    if near.character is None:
        for reason in near.blockers or reasons:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    typer.echo(f"closest card differs by {near.distance} across the requested stats", err=True)
    for difference in near.differences:
        typer.echo(f"  {difference}", err=True)
    return near.character


@app.command()
def decode(
    barcode: Annotated[str, typer.Argument(help="8 or 13 digit code.")],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Also print the card this barcode makes."),
    ] = None,
    name: Annotated[str, typer.Option("--name", help="Printed on the card only.")] = "Card",
    device: DeviceOption = Device.BB2,
    images: ImagesOption = None,
    print_shop: PrintShopOption = False,
) -> None:
    """Read a barcode the way the device reads it.

    Any product barcode is a card, which is how the device was played: read
    what is printed on the shopping and print the card it makes.
    """
    if device is not Device.BB2:
        show = show_first if device is Device.BB1 else show_double
        show(barcode, output=output, name=name, images=images, print_shop=print_shop)
        return
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
    if output is not None:
        typer.echo(f"Name      {name}")
        card = GeneratedCard(name=name, barcode=character.barcode, character=character)
        write_cards((card,), output, images, sheet_layout(print_shop=print_shop))


@app.command()
def products(
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Print the chosen products.")
    ] = None,
    search: Annotated[
        str, typer.Option("--search", help="Only products whose name, brand or barcode matches.")
    ] = "",
    count: Annotated[
        int | None, typer.Option("--count", "-n", min=1, help="Take this many at random.")
    ] = None,
    seed: Annotated[int | None, typer.Option("--seed", help="Repeat an earlier handful.")] = None,
    images: ImagesOption = None,
    print_shop: PrintShopOption = False,
) -> None:
    """Browse or print real Japanese supermarket products as cards."""
    found = random_products(count, seed=seed) if count else search_products(search)
    if not found:
        typer.echo(f"nothing on the shelf matches {search!r}", err=True)
        raise typer.Exit(code=1)
    if output is None:
        for product in found:
            character = decode_barcode(product.barcode)
            typer.echo(
                f"{product.barcode}  {product.name}  "
                f"{race_label(product.kind).english}  "
                f"HP {character.hp} ST {character.st} DF {character.df}"
            )
        typer.echo(f"{len(found)} product(s)")
        return
    write_cards(product_cards(found), output, images, sheet_layout(print_shop=print_shop))


@app.command()
def kinds() -> None:
    """Print every kind of card the device knows, and what each one does."""
    for race in Race:
        label = race_label(race)
        typer.echo(f"{race.value}  {race.name.lower():18s} {label.english} / {label.japanese}")
        typer.echo(f"   {RACE_DESCRIPTIONS[race]}")


@app.command()
def cheat(
    output: OutputOption,
    name: Annotated[str, typer.Option("--name", help="Printed on the card only.")] = (
        DEFAULT_CHEAT_NAME
    ),
    items: Annotated[
        bool,
        typer.Option(
            "--items", help="Add the strongest weapon, armour, health, herbs and magic items."
        ),
    ] = False,
    device: DeviceOption = Device.BB2,
    images: ImagesOption = None,
    print_shop: PrintShopOption = False,
) -> None:
    """Print the strongest card the device will read. Nobody has to know."""
    if device is not Device.BB2:
        cheat = cheat_first if device is Device.BB1 else cheat_double
        cheat(name, items=items, output=output, images=images, print_shop=print_shop)
        return
    card = strongest_card(name)
    character = card.character
    typer.echo(f"{card.name}: HP {character.hp}, ST {character.st}, DF {character.df}")
    typer.echo(f"Fights with ST {character.fighting_st}, DF {character.fighting_df}")
    typer.echo(f"Ability {character.special.code:02d} {character.special.description}")
    extras = strongest_items() if items else ()
    for extra in extras:
        typer.echo(f"{_item_line(extra)}; {fit_line(character.job, extra.character)}")
    write_cards((card, *extras), output, images, sheet_layout(print_shop=print_shop))


def _item_line(card: GeneratedCard) -> str:
    """One line naming an item, what it carries, and the power it passes on."""
    carried_text = ", ".join(f"{tile.key} {tile.value}" for tile in stat_tiles(card.character))
    special = card.character.special
    return f"{card.name}: {carried_text}; ability {special.code:02d} {special.description}"


@app.command()
def official(
    output: Annotated[Path | None, typer.Option("--output", "-o", help="PDF to write.")] = None,
    set_name: Annotated[
        str | None,
        typer.Option("--set", help="One set, by the key --list prints."),
    ] = None,
    listing: Annotated[bool, typer.Option("--list", help="List the sets and stop.")] = False,
    images: ImagesOption = None,
    print_shop: PrintShopOption = False,
) -> None:
    """Print the cards Epoch released, as the community transcribed them."""
    if listing:
        _list_official()
        return
    if output is None:
        typer.echo("--output is required unless --list is given", err=True)
        raise typer.Exit(code=2)
    chosen = _official_set(set_name) if set_name is not None else None
    write_cards(official_cards(chosen), output, images, sheet_layout(print_shop=print_shop))


def _list_official() -> None:
    """Print each set, its printable count, and the transcriptions left out."""
    for official_set in OfficialSet:
        count = len(official_cards(official_set))
        typer.echo(
            f"{count:4d}  {official_set.name.lower():24s}  {official_set.english}, "
            f"read by the {official_set.device.english}"
        )
    typer.echo(f"{len(official_cards()):4d}  total printable")
    for entry in rejected_transcriptions():
        typer.echo(f"skipped {entry.barcode} {entry.name}: its check digit is wrong")


def _official_set(value: str) -> OfficialSet:
    """Resolve a set from its key, reporting the keys on a miss."""
    key = value.strip().upper().replace("-", "_").replace(" ", "_")
    try:
        return OfficialSet[key]
    except KeyError:
        known = ", ".join(official_set.name.lower() for official_set in OfficialSet)
        typer.echo(f"unknown set {value!r}; known sets: {known}", err=True)
        raise typer.Exit(code=2) from None


@app.command()
def abilities() -> None:
    """Print the published special ability table."""
    for code in range(MIN_CODE, MAX_CODE + 1):
        ability = SpecialAbility.from_code(code)
        typer.echo(f"{ability.code:02d}  {ability.description}")


@app.command()
def doctor() -> None:
    """Check that this machine can print a card the device will read."""
    sections = (("the machine", machine()), ("this package", package()))
    for heading, section in sections:
        typer.echo(f"\n{heading}")
        for finding in section:
            typer.echo(f"  {MARKS[finding.state]} {finding.name}: {finding.detail}")
    verdict = worst(tuple(finding for _, section in sections for finding in section))
    typer.echo("")
    typer.echo(VERDICTS[verdict], err=verdict is State.FAIL)
    if verdict is State.FAIL:
        raise typer.Exit(code=1)


@app.command()
def web(
    host: Annotated[str, typer.Option("--host", help="Interface to bind.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", min=1, max=65535)] = 8000,
    open_browser: Annotated[
        bool, typer.Option("--open/--no-open", help="Open the page once the server is up.")
    ] = True,
) -> None:
    """Run the web interface and open it, which is this program with pictures."""
    run, build = _require_web()
    address = f"http://{host}:{port}/"
    typer.echo(DISCLAIMER)
    typer.echo(f"the card maker is at {address}")
    if open_browser:
        webbrowser.open(address)
    run(build(), host=host, port=port)


@app.command()
def serve(
    host: Annotated[str, typer.Option("--host", help="Interface to bind.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", min=1, max=65535)] = 8000,
) -> None:
    """Run the local web interface without opening a browser."""
    run, build = _require_web()
    typer.echo(DISCLAIMER)
    run(build(), host=host, port=port)


def _require_web() -> tuple[Callable[..., None], Callable[[], object]]:
    """Load the optional web dependencies, or say which extra is missing."""
    try:
        return _web_server()
    except ImportError as error:
        typer.echo("the web interface needs the ui extra: uv sync --extra ui", err=True)
        raise typer.Exit(code=1) from error


def _web_server() -> tuple[Callable[..., None], Callable[[], object]]:
    """Import the optional web dependencies only when the server is asked for."""
    import uvicorn  # noqa: PLC0415

    from maeyomi.ui.app import create_app  # noqa: PLC0415

    return uvicorn.run, create_app
