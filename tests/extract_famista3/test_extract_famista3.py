"""Tests for the tool that writes Famista 3's player tables from its ROM.

No ROM is committed, so these build a blank image, plant the pointer tables and
one batter and one pitcher where the game keeps them, and check the tool reads
them from the bytes.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_famista3.py"
ROM_SIZE = 0x40000
BATTER = bytes.fromhex("0300414000180123 0e".replace(" ", ""))
PITCHER = bytes.fromhex("0080555000220176809402010 50a".replace(" ", ""))


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_famista3", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def words(values: list[int]) -> bytes:
    return b"".join(value.to_bytes(2, "little") for value in values)


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    code = tool.CODE_BANK * tool.BANK_SIZE - tool.BANK_START
    rom[code + tool.SIZES : code + tool.SIZES + 2] = bytes([9, 14])
    rom[code + tool.KINDS : code + tool.KINDS + 4] = words([0x4573, 0x4587])
    rom[code + 0x4573 : code + 0x4573 + 20] = words([0x4000] * 3 + [0x47AA] * 7)
    rom[code + 0x4587 : code + 0x4587 + 20] = words([0x6000] * 10)
    data = tool.DATA_BANK * tool.BANK_SIZE - tool.BANK_START
    rom[data + 0x47AA : data + 0x47AA + len(BATTER)] = BATTER
    rom[data + 0x6000 + 14 : data + 0x6000 + 14 + len(PITCHER)] = PITCHER
    return bytes(rom)


def test_each_digit_names_its_group_of_players() -> None:
    tool = load()

    groups = tool.groups(planted(tool), 0)

    assert groups == ((0x4000, 0x47AA), (0, 0, 0, 1, 1, 1, 1, 1, 1, 1))


def test_a_batter_is_read_as_side_average_home_runs_and_speed() -> None:
    tool = load()

    batter = tool.player(planted(tool), 0x47AA, batter=True)

    assert batter == (0, 280, 35, 14)


def test_a_pitcher_is_read_as_side_era_speed_and_stamina() -> None:
    tool = load()

    pitcher = tool.player(planted(tool), 0x6000 + 14, batter=False)

    assert pitcher == (0, 290, 148, 10)


def test_the_tables_are_read_from_the_bytes() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "SIZES: Final = (9, 14)" in text
    assert "BATTER_GROUPS: Final = (0, 0, 0, 1, 1, 1, 1, 1, 1, 1)" in text
    assert "BATTERS: Final = (((0, 0, 0, 0)," in text
    assert "PITCHERS: Final = (((0, 0, 0, 0), (0, 290, 148, 10)," in text
