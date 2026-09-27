"""The commands, run against Datach Dragon Ball Z.

`main` hands over here when `--device dbz` is given. The game reads a fighter
or an item with a name, a level and three numbers, so this module maps the
shared options onto those: `--hp` is HP, `--bp` is BP and `--dp` is DP, and
the two options only this game reads, `--character` and `--level`, are
refused on every other device rather than silently ignored.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import typer

from maeyomi.cli.common import sheet_layout, write_cards
from maeyomi.cli.report import comparison_table
from maeyomi.datach.dbz import DbzCard, DbzKind, decode_dbz
from maeyomi.datach.dbz_cheat import strongest_dbz_card, strongest_dbz_items
from maeyomi.datach.dbz_names import FIGHTERS, ITEMS, fighter_name, item_entry
from maeyomi.datach.dbz_solve import DbzRequest, solve_dbz
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.rendering.export import ImageFormat

UNKNOWN: Final = "unknown"
NONE: Final = "none"
NOT_READ: Final = (
    "Datach Dragon Ball Z does not read {option}; it reads a name, a level, HP, BP, DP"
)
ONLY_DBZ: Final = "only --device dbz reads --character and --level"


def show_dbz(
    barcode: str, *, output: Path | None, name: str, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print what the game reads, and the card when asked."""
    try:
        card = decode_dbz(barcode)
    except BarcodeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    for line in describe_dbz(card):
        typer.echo(line)
    if output is not None:
        printable = GeneratedCard(name=name, barcode=card.barcode, character=card)
        write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def describe_dbz(card: DbzCard) -> list[str]:
    """One line per field the game shows: an item's effect, or a fighter's numbers."""
    head = [
        f"Device    {Device.DATACH_DBZ.english}",
        f"Barcode   {card.barcode}",
        f"Kind      {card.kind.value}",
        f"Name      {_name(card)}",
    ]
    if card.kind is DbzKind.ITEM:
        entry = item_entry(card.character)
        return [*head, f"Effect    {UNKNOWN if entry is None else entry.effect}"]
    return [
        *head,
        f"Level     {NONE if card.level is None else card.level}",
        f"HP        {card.hp}",
        f"BP        {card.bp}",
        f"DP        {card.dp}",
    ]


def refuse_dbz_options(character: str | None, level: int | None) -> None:
    """Stop when an option only this game reads was given for another device."""
    if character is not None or level is not None:
        typer.echo(ONLY_DBZ, err=True)
        raise typer.Exit(code=2)


@dataclass(frozen=True, slots=True)
class DbzPick:
    """The options only this game reads, and the one it refuses."""

    character: str | None = None
    level: int | None = None
    back_read: bool = False


def generate_dbz(
    request: CardRequest,
    pick: DbzPick,
    *,
    output: Path,
    images: ImageFormat | None,
    print_shop: bool,
) -> None:
    """Build one card to order, or say which field blocks it."""
    _refuse_unread(request, back_read=pick.back_read)
    wanted = _dbz_request(request, _character_id(pick.character), pick.level)
    outcome = solve_dbz(wanted)
    if outcome.card is None:
        for reason in outcome.blockers:
            typer.echo(reason, err=True)
        raise typer.Exit(code=1)
    for line in _comparison(wanted, outcome.card):
        typer.echo(line)
    typer.echo("")
    printable = GeneratedCard(
        name=request.name, barcode=outcome.card.barcode, character=outcome.card
    )
    write_cards((printable,), output, images, sheet_layout(print_shop=print_shop))


def cheat_dbz(
    name: str, *, items: bool, output: Path, images: ImageFormat | None, print_shop: bool
) -> None:
    """Print the strongest fighter, and the strongest item of each effect when asked."""
    fighter = strongest_dbz_card(name)
    card = fighter.character
    typer.echo(
        f"{fighter.name}: {_name(card, english_only=True)}, level {card.level}, "
        f"HP {card.hp}, BP {card.bp}, DP {card.dp}"
    )
    extras = strongest_dbz_items() if items else ()
    for extra in extras:
        entry = ITEMS[extra.character.character]
        typer.echo(f"{extra.name}: {entry.effect}")
    write_cards((fighter, *extras), output, images, sheet_layout(print_shop=print_shop))


def _refuse_unread(request: CardRequest, *, back_read: bool) -> None:
    """Stop on any option the game has no field for."""
    unread = {
        "--race": request.race is not None,
        "--class": request.character_class is not None,
        "--job": request.job is not None,
        "--speed": request.speed is not None,
        "--ability": request.special is not None,
        "--herbs": request.pp != Constraint.anything(),
        "--magic": request.mp != Constraint.anything(),
        "--back-read": back_read,
    }
    given = [option for option, present in unread.items() if present]
    if given:
        typer.echo(NOT_READ.format(option=", ".join(given)), err=True)
        raise typer.Exit(code=2)


def _dbz_request(request: CardRequest, character: int | None, level: int | None) -> DbzRequest:
    """The game's request: HP as asked, the attack option as BP and defence as DP."""
    kind = DbzKind.ITEM if character in ITEMS else DbzKind.FIGHTER
    return DbzRequest(
        character=character,
        kind=kind,
        level=level,
        hp=request.hp,
        bp=request.st,
        dp=request.df,
        name=request.name,
    )


def _character_id(value: str | None) -> int | None:
    """A character or item id from its number or its English or Japanese name."""
    if value is None:
        return None
    wanted = value.strip().casefold()
    if wanted.isdigit():
        return int(wanted)
    names = [
        (identifier, english, japanese) for identifier, (english, japanese) in FIGHTERS.items()
    ]
    names += [(identifier, item.english, item.japanese) for identifier, item in ITEMS.items()]
    found = [identifier for identifier, *known in names if wanted in {n.casefold() for n in known}]
    if not found:
        typer.echo(f"unknown character {value!r}; give a name the game shows or an id", err=True)
        raise typer.Exit(code=2)
    return min(found)


def _comparison(request: DbzRequest, card: DbzCard) -> list[str]:
    """Requested beside generated, for every field the card carries."""
    wanted = "-" if request.character is None else str(request.character)
    rows = [("Name", wanted, str(card.character))]
    if card.kind is DbzKind.FIGHTER:
        rows += [
            ("Level", "-" if request.level is None else str(request.level), str(card.level)),
            ("HP", str(request.hp), str(card.hp)),
            ("BP", str(request.bp), str(card.bp)),
            ("DP", str(request.dp), str(card.dp)),
        ]
    return comparison_table(rows)


def _name(card: DbzCard, *, english_only: bool = False) -> str:
    """A fighter's or item's name as the game shows it, with its English."""
    if card.kind is DbzKind.ITEM:
        entry = item_entry(card.character)
        names = None if entry is None else (entry.english, entry.japanese)
    else:
        names = fighter_name(card.character)
    if names is None:
        return f"{UNKNOWN} {card.character}"
    return names[0] if english_only else f"{names[0]} / {names[1]}"
