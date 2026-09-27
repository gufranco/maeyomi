"""Tests for the page behaviour carried over from fdstoolkit: wiring, not rendering.

What these produce in a browser is checked by tools/render/layout.e2e.mjs.
"""

import re

from maeyomi.ui.app import STATIC_DIR

MARKUP = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
UX = (STATIC_DIR / "ux.js").read_text(encoding="utf-8")
APP = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
DICTIONARIES = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")


def test_the_behaviour_loads_before_the_page_script() -> None:
    assert MARKUP.index("/static/ux.js") < MARKUP.index("/static/app.js")


def test_number_fields_are_checked_in_the_page_language() -> None:
    assert "novalidate" in UX
    for key in ("valid.number", "valid.range", "valid.step"):
        assert f"t('{key}'" in UX
        assert DICTIONARIES.count(f"'{key}':") == 2


def test_every_request_button_is_marked_busy() -> None:
    assert "toggleAttribute('disabled'" not in APP
    assert len(re.findall(r"setBusy\(button, (?:true|false)\)", APP)) == 6


def test_the_chosen_tab_is_kept_in_the_address() -> None:
    assert "rememberTab(" in APP
    assert "tabFromHash()" in APP
    assert "hashchange" in APP


def test_japanese_product_names_are_marked_as_japanese() -> None:
    assert '<span class="shelf-name" lang="ja">' in APP


def test_the_supermarket_searches_as_you_type() -> None:
    assert "setUpSearchAsYouType($('shop-query'), searchShelf)" in APP
