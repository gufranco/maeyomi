"""Tests for the served page and its static files.

These assert structure and wiring. What the page looks like once a browser has
laid it out is checked against a real engine, and the measurements are recorded
in the change that introduced it.
"""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from barcode_battler.ui.app import STATIC_DIR, create_app

MARKUP = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
SCRIPT = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
STYLES = (STATIC_DIR / "app.css").read_text(encoding="utf-8")


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app())


def test_every_static_file_is_present() -> None:
    for name in ("index.html", "app.css", "app.js"):
        assert (STATIC_DIR / name).is_file()


def test_the_static_files_are_served(client: TestClient) -> None:
    for name in ("app.css", "app.js"):
        assert client.get(f"/static/{name}").status_code == 200


def test_the_markup_is_a_complete_document() -> None:
    assert MARKUP.startswith("<!doctype html>")
    assert MARKUP.rstrip().endswith("</html>")


def test_the_page_declares_a_language_and_a_viewport() -> None:
    assert '<html lang="en">' in MARKUP
    assert 'name="viewport"' in MARKUP


def test_the_disclaimer_is_in_the_markup_rather_than_fetched(client: TestClient) -> None:
    assert "__DISCLAIMER__" in MARKUP
    assert "not been tested on a physical" in client.get("/").text
    assert "/api/about" not in SCRIPT


def test_the_placeholder_is_replaced_when_the_page_is_served(client: TestClient) -> None:
    assert "__DISCLAIMER__" not in client.get("/").text


@pytest.mark.parametrize(
    "endpoint",
    ["/api/generate", "/api/preview", "/api/sheet", "/api/sheet-preview", "/api/random"],
)
def test_the_script_calls_every_endpoint_it_needs(endpoint: str) -> None:
    assert endpoint in SCRIPT


@pytest.mark.parametrize(
    "control",
    ["name", "race", "class", "hp", "st", "df", "ability", "speed", "job", "count", "seed"],
)
def test_every_control_exists(control: str) -> None:
    assert f'id="{control}"' in MARKUP


def test_every_input_has_a_label_or_an_aria_label() -> None:
    ids = set(re.findall(r'<(?:input|select)[^>]*\bid="([^"]+)"', MARKUP))
    labelled = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', MARKUP))
    self_labelled = set(re.findall(r'<(?:input|select)[^>]*\bid="([^"]+)"[^>]*aria-label=', MARKUP))
    wrapped = set(re.findall(r'<label[^>]*>\s*<input[^>]*\bid="([^"]+)"', MARKUP, re.DOTALL))

    assert ids - labelled - self_labelled - wrapped == set()


def test_the_choices_are_filled_from_the_api_rather_than_typed_into_the_page() -> None:
    race_select = MARKUP.split('id="race"')[1].split("</select>")[0]

    assert "<option" not in race_select
    assert "/api/races" in SCRIPT
    assert "/api/abilities" in SCRIPT


def test_the_page_declares_its_own_focus_indicator() -> None:
    assert ":focus-visible" in STYLES
    assert "outline: 3px solid" in STYLES


def test_the_styles_define_a_dark_scheme_that_a_light_override_can_win() -> None:
    assert "prefers-color-scheme: dark" in STYLES
    assert ':root:not([data-theme="light"])' in STYLES
    assert ':root[data-theme="dark"]' in STYLES


def test_every_control_meets_the_minimum_target_size() -> None:
    assert STYLES.count("min-height: 44px") >= 4


def test_the_tabs_carry_their_roles() -> None:
    assert 'role="tablist"' in MARKUP
    assert MARKUP.count('role="tab"') == 2
    assert MARKUP.count('role="tabpanel"') == 2


def test_the_preview_regions_announce_their_updates() -> None:
    assert MARKUP.count('aria-live="polite"') == 2


def test_the_script_escapes_text_it_puts_into_markup() -> None:
    assert "escapeHtml" in SCRIPT
    assert "&lt;" in SCRIPT


def test_the_printing_advice_is_shown(client: TestClient) -> None:
    assert "fit to page" in client.get("/").text


def test_no_placeholder_survives_in_any_static_file() -> None:
    assert "__DISCLAIMER__" not in SCRIPT
    assert "__DISCLAIMER__" not in STYLES


def test_the_static_directory_is_inside_the_package() -> None:
    assert STATIC_DIR.name == "static"
    assert STATIC_DIR.parent.name == "ui"
    assert Path(STATIC_DIR).is_dir()
