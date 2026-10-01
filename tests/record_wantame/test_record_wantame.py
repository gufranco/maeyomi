"""Tests for the recorder that runs Wantame Music Channel's own checks, without running them.

How a code becomes the bits and check value the scanner sends, and how the
game's answers are recorded, are checked here against the example in GBE+'s
notes; running the game's routines needs the game and the Unicorn engine, so
recording runs by hand.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_wantame.py"
EXAMPLE = "011128531729"


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("record_wantame", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_code_is_sent_as_six_values_with_the_first_in_the_highest_bits() -> None:
    assert load().sent(EXAMPLE) == 0x8B38D489D


def test_the_check_value_is_the_code_128_checksum() -> None:
    assert load().check(EXAMPLE) == 0x41


def test_a_wrong_check_value_differs_from_the_right_one() -> None:
    tool = load()

    assert tool.wrong(EXAMPLE) != tool.check(EXAMPLE)
    assert tool.wrong(EXAMPLE) in range(tool.MODULUS)


def test_a_card_is_recorded_with_its_kind_and_place() -> None:
    reading = load().reading(EXAMPLE, (True, True, (1, 11)))

    assert reading == {
        "barcode": EXAMPLE,
        "checked": True,
        "wrong_check_refused": True,
        "kind": 1,
        "index": 11,
    }


def test_a_code_no_card_carries_is_recorded_as_no_kind() -> None:
    reading = load().reading("019900000000", (True, True, None))

    assert (reading["kind"], reading["index"]) == (0, -1)
