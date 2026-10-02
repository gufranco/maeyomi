"""Tests for the tool that writes Densha Daishuugou's card list from MAME's software list."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_densha.py"
LISTING = """<?xml version="1.0"?>
<softwarelist name="sega_beena_cart" description="Sega Beena cartridges">
  <software name="other"><part name="card1" interface="sega_9h0_0008_card">
    <feature name="part_id" value="Card 1"/>
    <feature name="barcode" value="0x0de1"/></part></software>
  <software name="denshaca">
    <part name="cart" interface="sega_beena_cart"></part>
    <part name="card4" interface="sega_9h0_0008_card">
      <feature name="part_id" value="Card 4"/><feature name="barcode" value="0x0cd1"/></part>
    <part name="card51" interface="sega_9h0_0008_card">
      <feature name="part_id" value="Test Card 51"/>
      <feature name="barcode" value="0x0ddd"/></part>
  </software>
</softwarelist>
"""


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("extract_densha", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_card_of_the_game_is_read_with_its_number_and_bars() -> None:
    assert load().cards(LISTING) == ((4, "100010110011"), (51, "101110111011"))


def test_a_value_is_written_as_its_bars_the_lowest_bit_first() -> None:
    assert load().bars(0xCD1) == "100010110011"


def test_the_tables_module_lists_the_cards() -> None:
    text = load().render(LISTING)

    assert "CARDS: Final[tuple[tuple[int, str], ...]] = ((4, '100010110011')," in text
