"""Tests that every public description says what the README says.

The README is where the project describes itself to anyone who is not reading
the code. The same sentence also has to appear in the package metadata and on
the repository page, and several hand-maintained copies of one sentence drift
within a release or two. These read the README and compare.

The repository page is not a file, so it cannot be asserted here. It is checked
by `scripts/check-public-text.sh`, which asks GitHub.
"""

import re
import tomllib
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).parent.parent.parent
README: Final = ROOT / "README.md"
MANIFEST: Final = ROOT / "pyproject.toml"
PROJECT: Final = "maeyomi"
ASCII_MAX: Final = 127
JAPANESE_SHARE: Final = 0.4


def strapline() -> str:
    """The one sentence under the title, which every other copy is made from."""
    match = re.search(r"<strong>(.+?)</strong>", README.read_text(encoding="utf-8"))
    assert match is not None, "the README has no strapline"
    return match.group(1)


def test_the_readme_opens_with_one_sentence_saying_what_this_is() -> None:
    line = strapline()

    assert line.endswith(".")
    assert len(line) < 100


def test_the_package_metadata_repeats_the_readme() -> None:
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["project"]["description"] == strapline().rstrip(".")


def test_the_formula_description_is_one_homebrew_will_accept() -> None:
    line = strapline().rstrip(".")

    assert not line.endswith(".")
    assert not line.lower().startswith(("a ", "an ", "the ", "maeyomi"))
    assert len(line) <= 80


def test_the_pdf_metadata_repeats_the_readme() -> None:
    source = (ROOT / "src" / "maeyomi" / "rendering" / "document.py").read_text(encoding="utf-8")
    match = re.search(r'^SUBJECT: Final = "(.+)"$', source, re.MULTILINE)
    assert match is not None

    assert match.group(1) == strapline().rstrip(".")


def test_every_public_surface_calls_the_project_by_its_name() -> None:
    named = {
        "the PDF author": (
            ROOT / "src" / "maeyomi" / "rendering" / "document.py",
            r'AUTHOR: Final = "(.+)"',
        ),
        "the served page": (ROOT / "src" / "maeyomi" / "ui" / "app.py", r'FastAPI\(title="(.+?)"'),
    }
    for surface, (path, pattern) in named.items():
        match = re.search(pattern, path.read_text(encoding="utf-8"))
        assert match is not None, surface
        assert match.group(1) == PROJECT, surface


def test_the_page_heading_is_the_project_name_capitalised() -> None:
    source = (ROOT / "src" / "maeyomi" / "ui" / "static" / "i18n.js").read_text(encoding="utf-8")

    assert re.findall(r"    title: '(.+)',", source) == [PROJECT.capitalize()] * 2


def lede() -> str:
    source = (ROOT / "src" / "maeyomi" / "ui" / "static" / "i18n.js").read_text(encoding="utf-8")
    match = re.search(r"    lede:\n      '(.+?)' \+\n      '(.+?)',", source, re.DOTALL)
    assert match is not None, "the page has no English lede"
    return match.group(1) + match.group(2)


def test_the_page_says_what_the_readme_says_it_says() -> None:
    assert lede() in README.read_text(encoding="utf-8")


TRANSLATIONS: Final = {
    "README.ja.md": ROOT / "README.ja.md",
    "README.zh-Hans.md": ROOT / "README.zh-Hans.md",
    "README.zh-HK.md": ROOT / "README.zh-HK.md",
}
ALL_READMES: Final = [README, *TRANSLATIONS.values()]
SWITCHER_LINKS: Final = {
    "README.md": "[English](README.md)",
    "README.ja.md": "[日本語](README.ja.md)",
    "README.zh-Hans.md": "[简体中文](README.zh-Hans.md)",
    "README.zh-HK.md": "[繁體中文 (香港)](README.zh-HK.md)",
}


def test_every_translation_is_mostly_han_or_kana() -> None:
    # Arrange
    texts = {name: path.read_text(encoding="utf-8") for name, path in TRANSLATIONS.items()}

    # Act
    shares = {
        name: sum(1 for character in text if ord(character) > ASCII_MAX) / len(text)
        for name, text in texts.items()
    }

    # Assert
    assert all(share > JAPANESE_SHARE for share in shares.values()), shares


def test_every_readme_covers_the_same_ground() -> None:
    # Arrange
    readmes = ALL_READMES

    # Act
    sections = {
        path: len(re.findall(r"^## ", path.read_text(encoding="utf-8"), re.MULTILINE))
        for path in readmes
    }

    # Assert
    assert len(set(sections.values())) == 1, sections


def test_every_readme_shows_the_same_screenshots() -> None:
    # Arrange
    pattern = r'(?:src|srcset)="(assets/[^"]+)"'

    # Act
    found = {
        path: frozenset(re.findall(pattern, path.read_text(encoding="utf-8")))
        for path in ALL_READMES
    }

    # Assert
    assert len(set(found.values())) == 1, {
        str(path): sorted(shots) for path, shots in found.items()
    }


def test_each_readme_offers_every_other_language() -> None:
    # Arrange
    readmes = {"README.md": README, **TRANSLATIONS}

    # Act
    texts = {name: path.read_text(encoding="utf-8") for name, path in readmes.items()}

    # Assert
    assert all(
        SWITCHER_LINKS[other] in texts[name]
        for name in readmes
        for other in SWITCHER_LINKS
        if other != name
    ), "a switcher link is missing"
