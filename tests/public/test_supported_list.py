"""Tests that the README lists every machine and game the code supports.

The table is typed into both READMEs by hand, so a device added to the code
without a row, or a row left behind by a removed device, would go unnoticed.
These read each table and compare it with the device list.
"""

import re
from pathlib import Path
from typing import Final

import pytest

from maeyomi.models.device import Device

ROOT: Final = Path(__file__).parent.parent.parent
TABLES: Final = {
    "README.md": "## What it supports",
    "README.ja.md": "## 対応している本体とゲーム",
}


def table_of(readme: str) -> str:
    """The text of the supported-list section, up to the next heading."""
    text = (ROOT / readme).read_text(encoding="utf-8")
    start = text.index(TABLES[readme])
    end = text.index("\n## ", start + 1)
    return text[start:end]


@pytest.mark.parametrize("readme", list(TABLES))
def test_the_table_has_one_row_per_device_and_no_other(readme: str) -> None:
    keys = re.findall(r"^\|.*\| `([a-z0-9]+)` \|$", table_of(readme), re.MULTILINE)

    assert sorted(keys) == sorted(device.value for device in Device)


@pytest.mark.parametrize("readme", list(TABLES))
@pytest.mark.parametrize("device", list(Device), ids=lambda device: device.value)
def test_every_row_names_the_device_as_the_page_does(readme: str, device: Device) -> None:
    rows = [row for row in table_of(readme).splitlines() if row.endswith(f"| `{device.value}` |")]

    assert len(rows) == 1
    assert f"| {device.english} |" in rows[0]
    assert f"| {device.japanese} |" in rows[0]
