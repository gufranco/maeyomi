"""Tests for the served page."""

import re

import pytest

from barcode_battler.ui.page import PAGE


def test_the_page_is_a_complete_document() -> None:
    assert PAGE.startswith("<!doctype html>")
    assert PAGE.rstrip().endswith("</html>")


def test_the_page_declares_a_language_and_a_viewport() -> None:
    assert '<html lang="en">' in PAGE
    assert 'name="viewport"' in PAGE


def test_the_page_carries_the_hardware_disclaimer() -> None:
    assert "not been tested on a physical" in PAGE


@pytest.mark.parametrize("endpoint", ["/api/generate", "/api/sheet", "/api/random"])
def test_the_page_calls_every_endpoint_it_needs(endpoint: str) -> None:
    assert endpoint in PAGE


@pytest.mark.parametrize("field", ["name", "hp", "st", "df", "race", "class", "ability"])
def test_the_form_offers_every_attribute(field: str) -> None:
    assert f'name="{field}"' in PAGE


def test_no_brace_placeholder_survived_formatting() -> None:
    assert not re.search(r"\{[a-z_]+\}", PAGE)


def test_the_page_declares_its_own_focus_indicator() -> None:
    assert ":focus-visible" in PAGE
    assert "outline: 3px solid currentColor" in PAGE
