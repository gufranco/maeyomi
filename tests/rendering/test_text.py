"""Tests for setting English and Japanese text on a card."""

import pytest

from barcode_battler.rendering.text import (
    ELLIPSIS,
    JAPANESE_FONT,
    LATIN_BOLD_FONT,
    LATIN_FONT,
    fit_size,
    font_for,
    is_latin,
    text_width_mm,
    wrap,
)


def test_latin_text_is_set_in_the_latin_face() -> None:
    assert font_for("Fire Knight") == LATIN_FONT
    assert font_for("Fire Knight", bold=True) == LATIN_BOLD_FONT


def test_japanese_text_is_set_in_the_japanese_face() -> None:
    assert font_for("ロボット") == JAPANESE_FONT
    assert font_for("ロボット", bold=True) == JAPANESE_FONT


def test_accented_latin_counts_as_latin() -> None:
    assert is_latin("Cafeé")
    assert not is_latin("ロ")


def test_text_that_fits_keeps_its_size() -> None:
    assert fit_size("99", LATIN_BOLD_FONT, 50.0, 17.0) == 17.0


def test_text_that_does_not_fit_shrinks_to_the_width() -> None:
    size = fit_size("99900", LATIN_BOLD_FONT, 10.0, 17.0)

    assert size < 17.0
    assert text_width_mm("99900", LATIN_BOLD_FONT, size) == pytest.approx(10.0, abs=0.01)


def test_latin_text_breaks_between_words() -> None:
    lines = wrap("own attack increased by half", 20.0, font=LATIN_FONT, size_pt=8, max_lines=3)

    assert len(lines) > 1
    assert all(not line.startswith(" ") for line in lines)
    assert " ".join(lines) == "own attack increased by half"


def test_japanese_breaks_between_characters_even_with_a_space() -> None:
    font = font_for("自分の破壊力")
    text = "自分の破壊力１００％アップ 2倍剣"

    lines = wrap(text, 15.0, font=font, size_pt=8, max_lines=5)

    assert len(lines) > 1
    assert "".join(lines).replace(" ", "") == text.replace(" ", "")


def test_text_past_the_last_line_is_cut_and_marked() -> None:
    lines = wrap("one two three four five six seven", 12.0, font=LATIN_FONT, size_pt=8, max_lines=2)

    assert len(lines) == 2
    assert lines[-1].endswith(ELLIPSIS)


def test_one_word_wider_than_the_line_is_cut() -> None:
    lines = wrap("Hi " + "W" * 60, 20.0, font=LATIN_FONT, size_pt=8, max_lines=3)

    assert lines[0] == "Hi"
    assert lines[1].endswith(ELLIPSIS)


def test_empty_text_has_no_lines() -> None:
    assert wrap("", 20.0, font=LATIN_FONT, size_pt=8, max_lines=2) == []
