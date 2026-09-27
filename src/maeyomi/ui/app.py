"""A local web interface over the same solver the command line uses.

Nothing here decides anything. Every route parses its payload into a
`CardRequest`, hands it to the solver, and reports what came back, so the two
surfaces cannot drift apart.

The page is served as static files rather than built here, and every choice it
offers comes from an endpoint backed by an enum, so a race or an ability added
to the models appears in the interface without a second edit.

Handlers are module level rather than nested inside the factory, so each one
stays independently readable and testable.
"""

import base64
import tempfile
from collections.abc import Sequence
from importlib import resources
from pathlib import Path
from typing import Final

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from maeyomi.cli.parsing import parse_character_class, parse_constraint, parse_race
from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import BarcodeError
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME, strongest_card
from maeyomi.generator.device_random import random_for
from maeyomi.generator.nearest import solve_nearest
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, CardResult, GeneratedCard
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from maeyomi.official.catalogue import (
    OfficialSet,
    device_cards,
    official_cards,
    rejected_transcriptions,
    sets_for,
)
from maeyomi.products.japan import (
    SHELF_LICENCE,
    SHELF_SOURCE,
    JapaneseProduct,
    japanese_products,
    search_products,
)
from maeyomi.products.lookup import ProductLookupError, look_up_name
from maeyomi.registry import (
    DeviceChoice,
    build_as,
    cheat_as,
    device_named,
    printable_as,
    read_as,
    readable_as,
    speed_note,
)
from maeyomi.rendering.face import summary_of
from maeyomi.rendering.labels import UNREADABLE, UNREADABLE_KIND, Bilingual
from maeyomi.rendering.preview import card_png, sheet_png_pages
from maeyomi.rendering.sheet import write_sheet
from maeyomi.ui.devices import dbz_choices, device_views, facts_of
from maeyomi.ui.schemas import (
    AbilityView,
    BarcodeSheetSpec,
    CardSpec,
    CharacterView,
    CheatResult,
    CheatSpec,
    DbzChoiceView,
    DeviceCardSpec,
    DeviceCheatSpec,
    DeviceReading,
    DeviceView,
    GenerateResult,
    LookupResult,
    OfficialCatalogue,
    OfficialSetView,
    OfficialSpec,
    PreviewSpec,
    ProductShelf,
    ProductView,
    RaceView,
    RandomSpec,
    RejectedView,
    SheetPreview,
    SheetSpec,
)

BAD_REQUEST: Final = 400
UNPROCESSABLE: Final = 422
STATIC_DIR: Final = Path(str(resources.files("maeyomi.ui") / "static"))
PREVIEW_PAGE_LIMIT: Final = 4
CARDS_PER_PAGE: Final = 9
SHELF_PAGE: Final = 60


def index() -> HTMLResponse:
    """Serve the page."""
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


def races() -> list[RaceView]:
    """Serve every kind of card, named for someone who has not read the manual."""
    return [RaceView.of(race) for race in Race]


def abilities() -> list[AbilityView]:
    """Serve the published ability table."""
    return [
        AbilityView.of(SpecialAbility.from_code(code)) for code in range(MIN_CODE, MAX_CODE + 1)
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
    reading = ReadType.BACK if spec.back_read else ReadType.FRONT
    outcome = solve(request, read_type=reading)
    if outcome.barcode is not None and outcome.character is not None:
        return GenerateResult(
            barcode=outcome.barcode,
            character=CharacterView.of(outcome.character),
            mismatches=[str(mismatch) for mismatch in outcome.mismatches],
            searched=outcome.searched,
        )
    if not spec.nearest or spec.back_read:
        raise HTTPException(status_code=UNPROCESSABLE, detail=list(outcome.blockers))
    near = solve_nearest(request)
    if near.barcode is None or near.character is None:
        raise HTTPException(
            status_code=UNPROCESSABLE, detail=list(near.blockers or outcome.blockers)
        )
    return GenerateResult(
        barcode=near.barcode,
        character=CharacterView.of(near.character),
        mismatches=[],
        searched=near.searched,
        is_exact=False,
        distance=near.distance,
        differences=list(near.differences),
    )


def preview(spec: PreviewSpec) -> Response:
    """Draw one card exactly as it would print, and return it as an image."""
    return Response(content=card_png(_decoded_card(spec)), media_type="image/png")


def sheet_preview(spec: RandomSpec) -> SheetPreview:
    """Draw the first pages of a random sheet, as images the page can show."""
    cards = _random_cards(spec)
    pages = sheet_png_pages(cards[: PREVIEW_PAGE_LIMIT * CARDS_PER_PAGE])
    return SheetPreview(count=len(cards), pages=[_data_url(page) for page in pages])


def sheet(spec: SheetSpec) -> FileResponse:
    """Build a sheet from an explicit list of cards."""
    if not spec.cards:
        raise HTTPException(status_code=UNPROCESSABLE, detail="no cards were requested")
    return _sheet_response([_solve_card(card) for card in spec.cards], "card.pdf")


def random_sheet(spec: RandomSpec) -> FileResponse:
    """Build a sheet of random cards."""
    return _sheet_response(_random_cards(spec), "cards.pdf")


def cheat(spec: CheatSpec) -> CheatResult:
    """The strongest card the device will read, under whatever name was typed."""
    card = strongest_card(spec.name or DEFAULT_CHEAT_NAME)
    return CheatResult(
        name=card.name, barcode=card.barcode, character=CharacterView.of(card.character)
    )


def barcode_sheet(spec: BarcodeSheetSpec) -> FileResponse:
    """Build a sheet from cards that already carry a barcode."""
    if not spec.cards:
        raise HTTPException(status_code=UNPROCESSABLE, detail="no cards were requested")
    return _sheet_response([_decoded_card(card) for card in spec.cards], "cards.pdf")


def official(device: str = "bb2") -> OfficialCatalogue:
    """The official sets of one device, how many of their cards print, and which were left out."""
    chosen = _device(device)
    sets = sets_for(chosen)
    return OfficialCatalogue(
        sets=[
            OfficialSetView(
                key=official_set.name.lower(),
                english=official_set.english,
                japanese=official_set.value,
                count=len(official_cards(official_set)),
            )
            for official_set in sets
        ],
        total=len(device_cards(chosen)),
        rejected=[
            RejectedView(
                barcode=entry.barcode,
                name=entry.name,
                reason="the check digit does not match the other twelve digits",
            )
            for entry in rejected_transcriptions()
            if entry.official_set in sets
        ],
    )


def official_sheet(spec: OfficialSpec) -> FileResponse:
    """Download one official set, or all of them."""
    return _sheet_response(_official_cards(spec), "official-cards.pdf")


def official_preview(spec: OfficialSpec) -> SheetPreview:
    """Draw the first pages of an official set."""
    cards = _official_cards(spec)
    pages = sheet_png_pages(cards[: PREVIEW_PAGE_LIMIT * CARDS_PER_PAGE])
    return SheetPreview(count=len(cards), pages=[_data_url(page) for page in pages])


def products(q: str = "", limit: int = SHELF_PAGE, device: str = "bb2") -> ProductShelf:
    """The shelf, or the part of it that matches what was typed, read by the chosen device."""
    chosen = _device(device)
    found = search_products(q)
    return ProductShelf(
        products=[_product_view(product, chosen) for product in found[: max(1, limit)]],
        total=len(japanese_products()),
        source=SHELF_SOURCE,
        licence=SHELF_LICENCE,
    )


def lookup(barcode: str) -> LookupResult:
    """Ask the open product database what a barcode is called."""
    try:
        name = look_up_name(barcode)
    except BarcodeError as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    except ProductLookupError:
        return LookupResult(barcode=barcode)
    return LookupResult(barcode=barcode, name=name)


def _product_view(product: JapaneseProduct, device: Device) -> ProductView:
    """Read a product the way the chosen device does, so the page shows what it becomes."""
    card = readable_as(device, product.barcode)
    if card is None:
        return _unreadable_view(product)
    shown = summary_of(card)
    note = speed_note(device, product.barcode) or Bilingual("", "")
    return ProductView(
        barcode=product.barcode,
        name=product.name,
        brand=product.brand,
        kind=shown.kind,
        label=shown.label.english,
        label_ja=shown.label.japanese,
        stats=shown.stats.english,
        stats_ja=shown.stats.japanese,
        effect=shown.effect.english,
        effect_ja=shown.effect.japanese,
        note=note.english,
        note_ja=note.japanese,
    )


def _unreadable_view(product: JapaneseProduct) -> ProductView:
    """A product whose barcode the chosen device's reader cannot read."""
    return ProductView(
        barcode=product.barcode,
        name=product.name,
        brand=product.brand,
        kind="unreadable",
        label=UNREADABLE_KIND.english,
        label_ja=UNREADABLE_KIND.japanese,
        stats=UNREADABLE.english,
        stats_ja=UNREADABLE.japanese,
        effect=UNREADABLE.english,
        effect_ja=UNREADABLE.japanese,
        readable=False,
    )


def devices() -> list[DeviceView]:
    """Every device and game the page can make cards for."""
    return device_views()


def dbz_characters() -> list[DbzChoiceView]:
    """Every fighter and item Datach Dragon Ball Z can produce."""
    return dbz_choices()


def read_on(device: str, barcode: str) -> DeviceReading:
    """Read a barcode the way the chosen device reads it."""
    card = _read(_device(device), barcode)
    return DeviceReading(barcode=card.barcode, facts=facts_of(card))


def device_card(spec: DeviceCardSpec) -> DeviceReading:
    """Build one card for the chosen device, or name every reason it cannot exist."""
    choice = DeviceChoice(
        back_read=spec.back_read,
        nearest=spec.nearest,
        character=spec.character,
        level=spec.level,
    )
    outcome = build_as(_device(spec.device), _request(spec), choice)
    if outcome.card is None:
        raise HTTPException(status_code=UNPROCESSABLE, detail=list(outcome.blockers))
    return DeviceReading(
        name=spec.name,
        barcode=outcome.card.barcode,
        facts=facts_of(outcome.card),
        is_exact=outcome.exact,
    )


def device_cheat(spec: DeviceCheatSpec) -> DeviceReading:
    """The strongest card the chosen device will read."""
    card = cheat_as(_device(spec.device), spec.name)
    return DeviceReading(name=card.name, barcode=card.barcode, facts=facts_of(card.character))


def create_app() -> FastAPI:
    """Build the application with every route attached."""
    app = FastAPI(title="maeyomi", docs_url="/docs")
    app.add_api_route("/", index, methods=["GET"], response_class=HTMLResponse)
    app.add_api_route("/api/races", races, methods=["GET"])
    app.add_api_route("/api/abilities", abilities, methods=["GET"])
    app.add_api_route("/api/decode/{barcode}", decode_one, methods=["GET"])
    app.add_api_route("/api/generate", generate_one, methods=["POST"])
    app.add_api_route("/api/preview", preview, methods=["POST"])
    app.add_api_route("/api/sheet-preview", sheet_preview, methods=["POST"])
    app.add_api_route("/api/sheet", sheet, methods=["POST"])
    app.add_api_route("/api/random", random_sheet, methods=["POST"])
    app.add_api_route("/api/cheat", cheat, methods=["POST"])
    app.add_api_route("/api/barcode-sheet", barcode_sheet, methods=["POST"])
    app.add_api_route("/api/official", official, methods=["GET"])
    app.add_api_route("/api/official-sheet", official_sheet, methods=["POST"])
    app.add_api_route("/api/official-preview", official_preview, methods=["POST"])
    app.add_api_route("/api/products", products, methods=["GET"])
    app.add_api_route("/api/lookup/{barcode}", lookup, methods=["GET"])
    app.add_api_route("/api/devices", devices, methods=["GET"])
    app.add_api_route("/api/dbz-characters", dbz_characters, methods=["GET"])
    app.add_api_route("/api/read/{device}/{barcode}", read_on, methods=["GET"])
    app.add_api_route("/api/device-card", device_card, methods=["POST"])
    app.add_api_route("/api/device-cheat", device_cheat, methods=["POST"])
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


def _random_cards(spec: RandomSpec) -> tuple[AnyCard, ...]:
    """Draw a batch for the chosen device, reporting a shortfall rather than a short one."""
    batch = random_for(_device(spec.device), spec.count, template=_request(spec), seed=spec.seed)
    if batch.shortfall:
        raise HTTPException(status_code=UNPROCESSABLE, detail=batch.reason)
    return batch.cards


def _data_url(png: bytes) -> str:
    """Wrap PNG bytes as a data URL the page can put straight into an image."""
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


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


def _decoded_card(spec: PreviewSpec) -> AnyCard:
    """Decode a card that already has a barcode the way its device reads it."""
    try:
        return printable_as(_device(spec.device), spec.barcode, spec.name)
    except BarcodeError as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error


def _read(device: Device, barcode: str) -> CardResult:
    """Decode with one device, reporting a code it refuses as a bad request."""
    try:
        return read_as(device, barcode)
    except BarcodeError as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error


def _device(key: str) -> Device:
    """The device a key names, reporting an unknown one."""
    try:
        return device_named(key)
    except ValueError as error:
        raise HTTPException(status_code=UNPROCESSABLE, detail=str(error)) from error


def _official_cards(spec: OfficialSpec) -> tuple[AnyCard, ...]:
    """The named set, or every set of the chosen device when none is named."""
    chosen = _official_set(spec)
    return device_cards(_device(spec.device)) if chosen is None else official_cards(chosen)


def _official_set(spec: OfficialSpec) -> OfficialSet | None:
    """Resolve the named set, or None for every set."""
    if spec.official_set is None:
        return None
    try:
        return OfficialSet[spec.official_set.strip().upper()]
    except KeyError as error:
        raise HTTPException(
            status_code=UNPROCESSABLE, detail=f"unknown set {spec.official_set!r}"
        ) from error


def _sheet_response(cards: Sequence[AnyCard], filename: str) -> FileResponse:
    """Render the cards to a temporary PDF and serve it as a download."""
    directory = Path(tempfile.mkdtemp(prefix="maeyomi-"))
    path = directory / filename
    write_sheet(cards, path)
    return FileResponse(path, media_type="application/pdf", filename=filename)
