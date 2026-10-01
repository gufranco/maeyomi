"""Tests for the recorder that runs Oshare Majo's own card decoder, without running it.

The memory layout, the input the decoder is handed and the parsing of what it
leaves behind are checked here; running the decoder needs the game and the
Unicorn engine, so recording runs by hand.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_oshare.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_oshare", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_decoder_is_handed_the_text_and_its_stop_padded_with_zeros() -> None:
    tool = load()

    handed = tool.handed("OUQV-9AU5JD")

    assert handed == b"OUQV-9AU5JD*" + bytes(tool.BUFFER_SIZE - 12)


def test_a_text_already_ending_in_its_stop_keeps_one() -> None:
    tool = load()

    assert tool.handed("OUQV-9AU5JD*") == tool.handed("OUQV-9AU5JD")


def test_an_item_the_decoder_names_is_read_up_to_its_end() -> None:
    assert load().item_of(1, b"DUP  CB004\x00\x03") == "DUP  CB004"


def test_a_refused_code_names_no_item() -> None:
    assert load().item_of(0, b"\x03\x00") == ""


def test_the_program_is_loaded_where_the_header_says() -> None:
    tool = load()
    rom = bytearray(0x5000)
    rom[0x20:0x24] = (0x4000).to_bytes(4, "little")
    rom[0x28:0x2C] = (0x2000000).to_bytes(4, "little")
    rom[0x2C:0x30] = (0x10).to_bytes(4, "little")
    rom[0x4000:0x4010] = b"0123456789abcdef"

    program = tool.program(bytes(rom))

    assert program == b"0123456789abcdef"
