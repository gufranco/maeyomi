"""Tests that the page says everything in both English and Japanese.

The dictionaries live in a script, so these read it as text: every key the
markup and the page script ask for must exist in both languages, the two
languages must carry the same keys, and every Japanese string must actually be
Japanese rather than an English string left untranslated.
"""

import re
from itertools import pairwise

import pytest

from maeyomi.ui.app import STATIC_DIR

MARKUP = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
SCRIPT = "".join(
    (STATIC_DIR / name).read_text(encoding="utf-8") for name in ("app.js", "devices.js")
)
DICTIONARIES = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
THE_SAME_IN_BOTH_LANGUAGES = {"title", "read.placeholder", "stat.pw", "stat.ust", "stat.usp"}


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
        if value.isascii() and key not in THE_SAME_IN_BOTH_LANGUAGES and not value.startswith("{")
    }

    assert untranslated == set()


def test_the_page_offers_both_languages() -> None:
    assert 'data-language="en"' in MARKUP
    assert 'data-language="ja"' in MARKUP


def test_the_language_choice_survives_storage_being_unavailable() -> None:
    assert DICTIONARIES.count("try {") >= 2
    assert "localStorage" in DICTIONARIES


def test_the_dictionaries_load_before_the_page_script() -> None:
    assert MARKUP.index("/static/i18n.js") < MARKUP.index("/static/devices.js")
    assert MARKUP.index("/static/devices.js") < MARKUP.index("/static/app.js")


def test_every_continued_string_belongs_to_a_key() -> None:
    lines = DICTIONARIES.splitlines()
    orphans = [
        number
        for number, (previous, line) in enumerate(pairwise(lines), start=2)
        if re.match(r"\s+'", line)
        and not re.match(r"\s+'[\w.]+':", line)
        and re.match(r"\s+('[\w.]+'|\w+): .+,$", previous)
    ]

    assert orphans == []
