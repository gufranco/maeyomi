"""Tests that every language the page speaks says everything English says.

The Chinese dictionaries live in their own files beside `i18n.js`. These load
each one with Node, as the browser would, and compare it with English key by
key, placeholder by placeholder.
"""

import json
import re
import shutil
import subprocess
from typing import Final

import pytest

from maeyomi.ui.app import STATIC_DIR

MARKUP: Final = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
DICTIONARIES: Final = {
    "zh-Hans": ("i18n-zh-hans.js", "MESSAGES_ZH_HANS"),
    "zh-Hant-HK": ("i18n-zh-hant-hk.js", "MESSAGES_ZH_HANT_HK"),
}
PLACEHOLDER: Final = re.compile(r"\{(\w+)\}")
LOADER: Final = """
const fs = require('fs');
const vm = require('vm');
const context = { navigator: {}, window: {}, document: {} };
vm.createContext(context);
for (const file of process.argv.slice(1)) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), context);
}
const script =
  'JSON.stringify({en: MESSAGES.en, zhHans: MESSAGES_ZH_HANS, zhHantHk: MESSAGES_ZH_HANT_HK})';
process.stdout.write(vm.runInContext(script, context));
"""


def messages() -> dict[str, dict[str, object]]:
    """Every dictionary, loaded by Node in the order the page loads them."""
    node = shutil.which("node")
    assert node is not None
    files = [str(STATIC_DIR / name) for name, _ in DICTIONARIES.values()]
    command = [node, "-e", LOADER, *files, str(STATIC_DIR / "i18n.js")]
    loaded = subprocess.run(command, capture_output=True, text=True, check=True)  # noqa: S603
    parsed: dict[str, dict[str, object]] = json.loads(loaded.stdout)
    return parsed


LOADED: Final = messages()
BY_LANGUAGE: Final = {"zh-Hans": LOADED["zhHans"], "zh-Hant-HK": LOADED["zhHantHk"]}


@pytest.mark.parametrize("language", list(DICTIONARIES))
def test_every_language_has_every_english_key(language: str) -> None:
    assert list(BY_LANGUAGE[language]) == list(LOADED["en"])


@pytest.mark.parametrize("language", list(DICTIONARIES))
def test_every_message_keeps_the_placeholders_of_its_english(language: str) -> None:
    translated = BY_LANGUAGE[language]

    mismatched = [
        key
        for key, english in LOADED["en"].items()
        if sorted(PLACEHOLDER.findall(json.dumps(english)))
        != sorted(PLACEHOLDER.findall(json.dumps(translated[key])))
    ]

    assert mismatched == []


@pytest.mark.parametrize("language", list(DICTIONARIES))
def test_the_page_offers_the_language_and_loads_its_words_first(language: str) -> None:
    script = f'<script src="/static/{DICTIONARIES[language][0]}"></script>'

    assert f'data-language="{language}"' in MARKUP
    assert MARKUP.index(script) < MARKUP.index('<script src="/static/i18n.js"></script>')
