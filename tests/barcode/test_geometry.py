"""Tests for the printed geometry of a barcode."""

import pytest

from maeyomi.barcode.geometry import (
    MAX_MODULE_WIDTH_MM,
    MIN_BAR_HEIGHT_MM,
    MIN_MODULE_WIDTH_MM,
    NOMINAL_BAR_HEIGHT_MM,
    NOMINAL_MODULE_WIDTH_MM,
    NOMINAL_TOTAL_HEIGHT_MM,
    TEXT_ZONE_MM,
    BarcodeGeometry,
)


def test_the_default_geometry_is_the_nominal_size() -> None:
    geometry = BarcodeGeometry()

    assert geometry.module_width_mm == NOMINAL_MODULE_WIDTH_MM
    assert geometry.bar_height_mm == NOMINAL_BAR_HEIGHT_MM


def test_the_drawn_height_clears_the_nominal_total() -> None:
    drawn = BarcodeGeometry().drawn_height_mm

    assert drawn >= NOMINAL_TOTAL_HEIGHT_MM
    assert drawn == pytest.approx(NOMINAL_BAR_HEIGHT_MM + TEXT_ZONE_MM)


def test_the_text_zone_is_the_measured_one_rather_than_the_published_difference() -> None:
    published = NOMINAL_TOTAL_HEIGHT_MM - NOMINAL_BAR_HEIGHT_MM

    assert published < TEXT_ZONE_MM


def test_a_truncated_bar_height_is_rejected() -> None:
    with pytest.raises(ValueError, match="truncates"):
        BarcodeGeometry(bar_height_mm=MIN_BAR_HEIGHT_MM - 0.01)


def test_the_eighty_percent_floor_is_accepted() -> None:
    assert BarcodeGeometry(bar_height_mm=MIN_BAR_HEIGHT_MM).bar_height_mm == MIN_BAR_HEIGHT_MM


def test_the_height_floor_is_eighty_percent_of_the_nominal() -> None:
    assert pytest.approx(NOMINAL_BAR_HEIGHT_MM * 0.8) == MIN_BAR_HEIGHT_MM


def test_a_module_width_below_the_standard_minimum_is_rejected() -> None:
    with pytest.raises(ValueError, match="module width"):
        BarcodeGeometry(module_width_mm=MIN_MODULE_WIDTH_MM - 0.01)


def test_a_module_width_above_the_standard_maximum_is_rejected() -> None:
    with pytest.raises(ValueError, match="module width"):
        BarcodeGeometry(module_width_mm=MAX_MODULE_WIDTH_MM + 0.01)


def test_a_zero_height_is_rejected() -> None:
    with pytest.raises(ValueError, match="truncates"):
        BarcodeGeometry(bar_height_mm=0)


def test_the_quiet_zones_are_expressed_in_modules_and_scale_with_the_module() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.5)

    assert geometry.left_quiet_zone_mm(13) == pytest.approx(11 * 0.5)
    assert geometry.right_quiet_zone_mm(13) == pytest.approx(7 * 0.5)


def test_an_eight_digit_code_has_seven_modules_of_quiet_zone_on_each_side() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.5)

    assert geometry.left_quiet_zone_mm(8) == pytest.approx(7 * 0.5)
    assert geometry.right_quiet_zone_mm(8) == pytest.approx(7 * 0.5)


def test_a_thirteen_digit_symbol_is_ninety_five_modules_wide_before_quiet_zones() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    assert geometry.symbol_width_mm(13) == pytest.approx(95 * 0.33)


def test_the_total_width_includes_both_quiet_zones() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    expected = (95 + 11 + 7) * 0.33

    assert geometry.total_width_mm(13) == pytest.approx(expected)


def test_an_unsupported_length_is_rejected() -> None:
    with pytest.raises(ValueError, match="8 or 13"):
        BarcodeGeometry().symbol_width_mm(12)
