"""Tests for the recorder that runs Mushiking's own card comparison, without running it.

The table the comparison reads, the order the lists are tried in and the
reading of a match are checked here; running the comparison needs the game
and the Unicorn engine, so recording runs by hand.
"""

import importlib.util
import struct
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_mushiking.py"


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("record_mushiking", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_table_points_each_list_at_its_place_in_the_file() -> None:
    tool = load()

    table = struct.unpack("<17I", tool.table())

    assert table[:3] == (tool.FILE_ADDRESS + 0x3667, tool.FILE_ADDRESS, 190)
    assert table[15:] == (tool.SIXTH_ADDRESS, tool.SEVENTH_ADDRESS)


def test_the_lists_are_tried_in_the_games_order() -> None:
    tool = load()

    tried = tool.attempts()

    assert tried[0] == (0x0201FBCC, 0, 0)
    assert tried[189] == (0x0201FBCC, 0, 189)
    assert tried[-1] == (0x0201FEB8, 6, 7)
    assert len(tried) == 190 + 60 + 29 + 239 + 6 + 3 + 8


def test_a_match_is_recorded_with_its_list_index_and_variant() -> None:
    assert load().reading((0, 189), 10) == {"list": 0, "index": 189, "variant": 10}


def test_no_match_is_recorded_as_no_list() -> None:
    assert load().reading(None, 0) == {"list": -1, "index": -1, "variant": 0}


def test_the_code_is_handed_with_room_after_it() -> None:
    tool = load()

    assert tool.handed("GRFCT20K03W02") == b"GRFCT20K03W02" + bytes(tool.BUFFER_SIZE - 13)
