"""Tests that the page says everything in both English and Japanese.

The dictionaries live in a script, so these read it as text: every key the
markup and the page script ask for must exist in both languages, the two
languages must carry the same keys, and every Japanese string must actually be
Japanese rather than an English string left untranslated.
"""

import re

import pytest

from barcode_battler.ui.app import STATIC_DIR

MARKUP = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
SCRIPT = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
DICTIONARIES = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
ENGLISH_ONLY = {"title"}


def _block(language: str) -> str:
    start = DICTIONARIES.index(f"  {language}: {{")
    depth = 0
    for index in range(start, len(DICTIONARIES)):
        if DICTIONARIES[index] == "{":
            depth += 1
        elif DICTIONARIES[index] == "}":
            depth -= 1
            if depth == 0:
                return DICTIONARIES[start:index]
    raise AssertionError(language)


def _keys(language: str) -> set[str]:
    block = _block(language)
    return set(re.findall(r"^    '?([\w.]+)'?:", block, re.MULTILINE))


def _values(language: str) -> dict[str, str]:
    block = _block(language)
    pairs = re.findall(r"^    '?([\w.]+)'?:\s*'((?:[^'\\]|\\.)*)'", block, re.MULTILINE)
    return dict(pairs)


def _used_keys() -> set[str]:
    markup = set(re.findall(r'data-i18n(?:-placeholder|-aria-label)?="([^"]+)"', MARKUP))
    script = set(re.findall(r"\bt\('([\w.]+)'", SCRIPT))
    return markup | script


def test_both_languages_carry_the_same_keys() -> None:
    assert _keys("en") == _keys("ja")


@pytest.mark.parametrize("language", ["en", "ja"])
def test_every_key_the_page_uses_exists(language: str) -> None:
    assert _used_keys() - _keys(language) == set()


def test_every_japanese_string_is_japanese() -> None:
    untranslated = {
        key
        for key, value in _values("ja").items()
        if value.isascii() and key not in ENGLISH_ONLY and not value.startswith("{")
    }

    assert untranslated == set()


def test_the_page_offers_both_languages() -> None:
    assert 'data-language="en"' in MARKUP
    assert 'data-language="ja"' in MARKUP


def test_the_language_choice_survives_storage_being_unavailable() -> None:
    assert DICTIONARIES.count("try {") >= 2
    assert "localStorage" in DICTIONARIES


def test_the_disclaimer_is_in_both_languages_without_a_script() -> None:
    assert "__DISCLAIMER__" in MARKUP
    assert "__DISCLAIMER_JA__" in MARKUP


def test_the_dictionaries_load_before_the_page_script() -> None:
    assert MARKUP.index("/static/i18n.js") < MARKUP.index("/static/app.js")
