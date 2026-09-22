"""Tests that every public description says what the README says.

The README is where the project describes itself to anyone who is not reading
the code. The same sentence also has to appear in the package metadata, in the
Homebrew formula and on the repository page, and four hand-maintained copies of
one sentence drift within a release or two. These read the README and compare.

The repository page is not a file, so it cannot be asserted here. It is checked
by `scripts/check-public-text.sh`, which asks GitHub.
"""

import re
import tomllib
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).parent.parent.parent
README: Final = ROOT / "README.md"
FORMULA: Final = ROOT / "Formula" / "maeyomi.rb"
MANIFEST: Final = ROOT / "pyproject.toml"


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


def test_the_formula_repeats_the_readme() -> None:
    match = re.search(r'^\s*desc "(.+)"$', FORMULA.read_text(encoding="utf-8"), re.MULTILINE)
    assert match is not None

    assert match.group(1) == strapline().rstrip(".")


def test_the_formula_description_is_one_homebrew_will_accept() -> None:
    line = strapline().rstrip(".")

    assert not line.endswith(".")
    assert not line.lower().startswith(("a ", "an ", "the ", "maeyomi"))
    assert len(line) <= 80
