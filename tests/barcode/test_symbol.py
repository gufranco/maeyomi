"""Tests for drawing an EAN symbol as vectors and reading it back."""

from collections import Counter
from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.geometry import (
    CODE39_MODULE_WIDTH_MM,
    MIN_BAR_HEIGHT_MM,
    NOMINAL_BAR_HEIGHT_MM,
    NOMINAL_TOTAL_HEIGHT_MM,
    BarcodeGeometry,
    Symbology,
)
from maeyomi.barcode.rasterise import ink_box, render_pdf_pages
from maeyomi.barcode.symbol import KeptCheckEan13, draw_symbol, kept_widget, symbol_size_mm
from maeyomi.barcode.verify import decode_pdf
from maeyomi.decoder.errors import (
    BarcodeError,
    CheckDigitError,
    InvalidCharacterError,
    InvalidLengthError,
    UnsupportedBarcodeError,
)
from maeyomi.rendering.card_style import CardStyle
from maeyomi.rendering.layout import CARD_WIDTH_MM

MARGIN_MM = 10.0
MEASURE_DPI = 600
INK_THRESHOLD = 128


def write_pdf(path: Path, code: str, geometry: BarcodeGeometry) -> tuple[float, float]:
    width, height = symbol_size_mm(code, geometry)
    canvas = Canvas(
        str(path), pagesize=((width + 2 * MARGIN_MM) * mm, (height + 2 * MARGIN_MM) * mm)
    )
    draw_symbol(canvas, code, x_mm=MARGIN_MM, y_mm=MARGIN_MM, geometry=geometry)
    canvas.showPage()
    canvas.save()
    return width, height


def bar_heights_mm(path: Path) -> list[float]:
    """Every column's tallest unbroken run of ink, in millimetres."""
    image = render_pdf_pages(path, dpi=MEASURE_DPI)[0].convert("L")
    width, height = image.size
    grey = image.tobytes()
    per_mm = MEASURE_DPI / 25.4
    runs: list[float] = []
    for x in range(width):
        best = run = 0
        for y in range(height):
            run = run + 1 if grey[y * width + x] < INK_THRESHOLD else 0
            best = max(best, run)
        if best:
            runs.append(best / per_mm)
    return runs


def data_bar_height_mm(path: Path) -> float:
    """The height of the ordinary data bars, which is the specification's bar height."""
    runs = bar_heights_mm(path)
    return min(runs, key=lambda value: abs(value - _mode(runs)))


def tallest_bar_height_mm(path: Path) -> float:
    """The height of the guard bars, which run past the data bars."""
    return max(bar_heights_mm(path))


def _mode(values: list[float]) -> float:
    """The most common measured height, rounded to a hundredth of a millimetre."""
    tally = Counter(round(value, 2) for value in values)
    return tally.most_common(1)[0][0]


def ink_size_mm(path: Path) -> tuple[float, float]:
    box = ink_box(render_pdf_pages(path, dpi=MEASURE_DPI)[0])
    assert box is not None
    per_mm = MEASURE_DPI / 25.4
    return (box[2] - box[0]) / per_mm, (box[3] - box[1]) / per_mm


def test_a_thirteen_digit_symbol_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "ean13.pdf"

    write_pdf(path, "0401207237501", BarcodeGeometry())

    assert decode_pdf(path) == ["0401207237501"]


def test_an_eight_digit_symbol_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "ean8.pdf"

    write_pdf(path, "49123456", BarcodeGeometry())

    assert decode_pdf(path) == ["49123456"]


@pytest.mark.parametrize("module_width", [0.264, 0.33, 0.45, 0.66])
def test_a_symbol_decodes_at_every_permitted_module_width(
    tmp_path: Path, module_width: float
) -> None:
    path = tmp_path / f"width-{module_width}.pdf"

    write_pdf(path, "0401207237501", BarcodeGeometry(module_width_mm=module_width))

    assert decode_pdf(path) == ["0401207237501"]


@pytest.mark.parametrize(("code", "length"), [("0401207237501", 13), ("49123456", 8)])
def test_the_drawn_width_is_at_least_the_standard_minimum(code: str, length: int) -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    width, _ = symbol_size_mm(code, geometry)

    assert width == pytest.approx(
        geometry.total_width_mm(length)
    ) or width > geometry.total_width_mm(length)


def test_a_thirteen_digit_symbol_is_the_exact_standard_width() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    width, _ = symbol_size_mm("0401207237501", geometry)

    assert width / geometry.module_width_mm == pytest.approx(113.0)


def test_the_drawn_height_clears_the_nominal_total() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    _, height = symbol_size_mm("0401207237501", geometry)

    assert height >= NOMINAL_TOTAL_HEIGHT_MM


def test_the_data_bars_reach_the_published_height(tmp_path: Path) -> None:
    path = tmp_path / "bars.pdf"
    geometry = BarcodeGeometry()

    write_pdf(path, "0401207237501", geometry)

    assert data_bar_height_mm(path) >= NOMINAL_BAR_HEIGHT_MM


def test_a_shorter_setting_still_clears_the_floor(tmp_path: Path) -> None:
    path = tmp_path / "short.pdf"
    geometry = BarcodeGeometry(bar_height_mm=MIN_BAR_HEIGHT_MM)

    write_pdf(path, "0401207237501", geometry)

    assert data_bar_height_mm(path) >= MIN_BAR_HEIGHT_MM * 0.98


def test_the_guard_bars_are_taller_than_the_data_bars(tmp_path: Path) -> None:
    path = tmp_path / "guards.pdf"

    write_pdf(path, "0401207237501", BarcodeGeometry())

    assert tallest_bar_height_mm(path) > data_bar_height_mm(path)


def test_the_bars_fit_inside_the_declared_width_leaving_the_quiet_zones_blank(
    tmp_path: Path,
) -> None:
    path = tmp_path / "quiet.pdf"
    geometry = BarcodeGeometry(show_digits=False)

    declared_width, _ = write_pdf(path, "0401207237501", geometry)
    ink_width, _ = ink_size_mm(path)

    assert ink_width < declared_width
    assert declared_width - ink_width >= geometry.right_quiet_zone_mm(13)


def test_the_human_readable_digits_are_printed_beside_the_bars(tmp_path: Path) -> None:
    with_digits = tmp_path / "with.pdf"
    without_digits = tmp_path / "without.pdf"

    write_pdf(with_digits, "0401207237501", BarcodeGeometry(show_digits=True))
    write_pdf(without_digits, "0401207237501", BarcodeGeometry(show_digits=False))

    assert ink_size_mm(with_digits)[0] > ink_size_mm(without_digits)[0]


def test_a_code_that_is_not_a_valid_barcode_is_rejected() -> None:
    with pytest.raises(ValueError, match="check digit"):
        symbol_size_mm("0401207237509", BarcodeGeometry())


def test_a_twelve_digit_code_is_rejected() -> None:
    with pytest.raises(ValueError, match="8 or 13"):
        symbol_size_mm("040120723750", BarcodeGeometry())


def test_a_symbol_told_to_keep_its_check_digit_draws_the_digit_it_was_given() -> None:
    geometry = BarcodeGeometry(kept_check=True)

    widget = kept_widget("0021495637396", geometry)

    assert isinstance(widget, KeptCheckEan13)
    assert widget.value + widget.drawn_check_digit == "0021495637396"


@pytest.mark.parametrize("code", ["00214956373A6", "002149563739"])
def test_a_kept_check_symbol_still_needs_thirteen_digits(code: str) -> None:
    with pytest.raises(BarcodeError):
        kept_widget(code, BarcodeGeometry(kept_check=True))


def test_a_wrong_check_digit_is_still_refused_unless_the_symbol_is_told_to_keep_it() -> None:
    with pytest.raises(CheckDigitError):
        symbol_size_mm("0021495637396", BarcodeGeometry())


def test_a_kept_check_digit_draws_the_same_width_as_a_correct_one() -> None:
    kept = symbol_size_mm("0021495637396", BarcodeGeometry(kept_check=True))

    assert kept == symbol_size_mm("0021495637397", BarcodeGeometry())


CODE39 = BarcodeGeometry(module_width_mm=CODE39_MODULE_WIDTH_MM, symbology=Symbology.CODE39)
CODE128 = BarcodeGeometry(symbology=Symbology.CODE128)
HCV_TEXT = "AA01C0RD00V01"
WAVE_CODE = "040000060019"


def test_a_code39_symbol_decodes_back_to_its_text(tmp_path: Path) -> None:
    path = tmp_path / "code39.pdf"
    write_pdf(path, HCV_TEXT, CODE39)

    found = decode_pdf(path)

    assert found == [HCV_TEXT]


def test_a_code39_text_framed_by_its_start_and_stop_reads_the_same(tmp_path: Path) -> None:
    path = tmp_path / "framed.pdf"
    write_pdf(path, f"*{HCV_TEXT}*", CODE39)

    found = decode_pdf(path)

    assert found == [HCV_TEXT]


def test_a_code39_symbol_fits_a_card() -> None:
    width, _ = symbol_size_mm(HCV_TEXT, CODE39)

    assert width < CARD_WIDTH_MM - 2 * CardStyle().padding_mm


def test_a_character_code39_cannot_carry_is_rejected() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="Code 39"):
        symbol_size_mm("aa01", CODE39)


def test_a_code128_symbol_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "code128.pdf"
    write_pdf(path, WAVE_CODE, CODE128)

    found = decode_pdf(path)

    assert found == [WAVE_CODE]


def test_a_code128_code_with_a_letter_is_rejected() -> None:
    with pytest.raises(InvalidCharacterError):
        symbol_size_mm("04000006001A", CODE128)


def test_a_code128_code_of_odd_length_is_rejected() -> None:
    with pytest.raises(InvalidLengthError):
        symbol_size_mm("04000006001", CODE128)
