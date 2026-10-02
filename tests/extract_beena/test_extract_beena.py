"""Tests for the tool that writes a stripe card game's card list from MAME's software lists."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_beena.py"
LISTING = """<?xml version="1.0"?>
<softwarelist name="sega_beena_cart" description="Sega Beena cartridges">
  <software name="other"><description>Other</description>
    <part name="card1" interface="sega_9h0_0008_card">
    <feature name="part_id" value="Card 1"/>
    <feature name="barcode" value="0x0de1"/></part></software>
  <software name="denshaca"><description>Densha Daishuugou! Card de Asobou</description>
    <part name="cart" interface="sega_beena_cart"></part>
    <part name="card4" interface="sega_9h0_0008_card">
      <feature name="part_id" value="Card 4"/>
      <feature name="barcode" value="0x0cd1"/></part>
    <part name="card51" interface="sega_9h0_0008_card">
      <feature name="part_id" value="Test Card 51 - Congratulations Screen"/>
      <feature name="barcode" value="0x0ddd"/></part>
  </software>
</softwarelist>
"""


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("extract_beena", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_card_of_the_game_is_read_with_its_number_and_bars() -> None:
    assert load().cards(LISTING, "denshaca", 12) == ((4, "100010110011"), (51, "101110111011"))


def test_a_game_the_list_does_not_have_has_no_cards() -> None:
    assert load().cards(LISTING, "missing", 12) == ()


def test_the_game_is_named_as_the_list_describes_it() -> None:
    tool = load()

    assert (tool.title(LISTING, "denshaca"), tool.title(LISTING, "missing")) == (
        "Densha Daishuugou! Card de Asobou",
        "",
    )


def test_a_value_is_written_as_its_bars_the_lowest_bit_first() -> None:
    assert load().bars(0xCD1, 12) == "100010110011"


def test_a_sixteen_place_value_keeps_its_high_places() -> None:
    assert load().bars(0x900A, 16) == "0101000000001001"


def test_the_tables_module_names_the_game_and_lists_the_cards() -> None:
    text = load().render(LISTING, "denshaca", 12)

    assert '"""The cards Densha Daishuugou! Card de Asobou reads.' in text
    assert "CARDS: Final[tuple[tuple[int, str], ...]] = ((4, '100010110011')," in text
    assert "its 12 bar" in text
    assert "hash/sega_beena_cart.xml" in text


def test_a_listing_with_no_name_names_no_list() -> None:
    assert load().list_name("<softwarelist>") == ""
