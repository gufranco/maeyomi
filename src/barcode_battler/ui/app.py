"""A local web interface over the same solver the command line uses.

Nothing here decides anything. Every route parses its payload into a
`CardRequest`, hands it to the solver, and reports what came back, so the two
surfaces cannot drift apart.

Handlers are module level rather than nested inside the factory, so each one
stays independently readable and testable.
"""

import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from barcode_battler.cli.parsing import parse_character_class, parse_constraint, parse_race
from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.errors import BarcodeError
from barcode_battler.generator.random_cards import generate_random
from barcode_battler.generator.solve import solve
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from barcode_battler.rendering.sheet import write_sheet
from barcode_battler.ui.page import PAGE
from barcode_battler.ui.schemas import (
    AbilityView,
    CardSpec,
    CharacterView,
    GenerateResult,
    RandomSpec,
    SheetSpec,
)

BAD_REQUEST: Final = 400
UNPROCESSABLE: Final = 422


def index() -> str:
    """Serve the single page."""
    return PAGE


def abilities() -> list[AbilityView]:
    """Serve the published ability table."""
    return [
        AbilityView(code=code, description=SpecialAbility.from_code(code).description)
        for code in range(MIN_CODE, MAX_CODE + 1)
    ]


def decode_one(barcode: str) -> CharacterView:
    """Read a barcode the way the device reads it."""
    try:
        return CharacterView.of(decode(barcode))
    except BarcodeError as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error


def generate_one(spec: CardSpec) -> GenerateResult:
    """Solve one card and report what it decodes to."""
    request = _request(spec)
    outcome = solve(request)
    if outcome.barcode is None or outcome.character is None:
        raise HTTPException(status_code=UNPROCESSABLE, detail=list(outcome.blockers))
    return GenerateResult(
        barcode=outcome.barcode,
        character=CharacterView.of(outcome.character),
        mismatches=[str(mismatch) for mismatch in outcome.mismatches],
        searched=outcome.searched,
    )


def sheet(spec: SheetSpec) -> FileResponse:
    """Build a sheet from an explicit list of cards."""
    if not spec.cards:
        raise HTTPException(status_code=UNPROCESSABLE, detail="no cards were requested")
    return _sheet_response([_solve_card(card) for card in spec.cards], "card.pdf")


def random_sheet(spec: RandomSpec) -> FileResponse:
    """Build a sheet of random cards."""
    batch = generate_random(spec.count, template=_request(spec), seed=spec.seed)
    if batch.shortfall:
        raise HTTPException(status_code=UNPROCESSABLE, detail=batch.reason)
    return _sheet_response(batch.cards, "cards.pdf")


def create_app() -> FastAPI:
    """Build the application with every route attached."""
    app = FastAPI(title="Barcode Battler II card generator", docs_url="/docs")
    app.add_api_route("/", index, methods=["GET"], response_class=HTMLResponse)
    app.add_api_route("/api/abilities", abilities, methods=["GET"])
    app.add_api_route("/api/decode/{barcode}", decode_one, methods=["GET"])
    app.add_api_route("/api/generate", generate_one, methods=["POST"])
    app.add_api_route("/api/sheet", sheet, methods=["POST"])
    app.add_api_route("/api/random", random_sheet, methods=["POST"])
    return app


def _request(spec: CardSpec) -> CardRequest:
    """Parse a payload into the same request the command line builds."""
    try:
        return CardRequest(
            name=spec.name,
            hp=parse_constraint(spec.hp),
            st=parse_constraint(spec.st),
            df=parse_constraint(spec.df),
            race=parse_race(spec.race),
            character_class=parse_character_class(spec.character_class),
            job=spec.job,
            speed=spec.speed,
            special=spec.ability,
        )
    except ValueError as error:
        raise HTTPException(status_code=UNPROCESSABLE, detail=str(error)) from error


def _solve_card(spec: CardSpec) -> GeneratedCard:
    """Solve one card or report why it cannot exist."""
    outcome = solve(_request(spec))
    if outcome.barcode is None or outcome.character is None:
        raise HTTPException(status_code=UNPROCESSABLE, detail=list(outcome.blockers))
    return GeneratedCard(name=spec.name, barcode=outcome.barcode, character=outcome.character)


def _sheet_response(cards: Sequence[GeneratedCard], filename: str) -> FileResponse:
    """Render the cards to a temporary PDF and serve it as a download."""
    directory = Path(tempfile.mkdtemp(prefix="barcode-battler-"))
    path = directory / filename
    write_sheet(cards, path)
    return FileResponse(path, media_type="application/pdf", filename=filename)
