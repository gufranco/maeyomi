"""Read the file system a Nintendo DS cartridge carries, for the DS extractors.

The cartridge header gives the offset of the file name table at 0x40 and of the
file allocation table at 0x48. The name table opens with one eight-byte entry
per directory: where its listing starts, the number of its first file, and its
parent. A listing is a run of names, each led by its length; a length with the
top bit set names a directory and is followed by that directory's number.
Files take numbers in listing order from the directory's first, and the
allocation table gives each file's start and end.
"""

from typing import Final

FIELD_SIZE: Final = 4
SHORT_SIZE: Final = 2
FNT_OFFSET_FIELD: Final = 0x40
FAT_OFFSET_FIELD: Final = 0x48
MAIN_ENTRY: Final = 8
FAT_ENTRY: Final = 8
DIRECTORY_FLAG: Final = 0x80
DIRECTORY_BASE: Final = 0xF000
MAX_DEPTH: Final = 8

type Path = tuple[str, ...]


def _number(rom: bytes, place: int, size: int = FIELD_SIZE) -> int:
    return int.from_bytes(rom[place : place + size], "little")


def _listing(rom: bytes, directory: int) -> list[tuple[str, int, bool]]:
    """The names in one directory, each with its file or directory number."""
    fnt = _number(rom, FNT_OFFSET_FIELD)
    entry = fnt + MAIN_ENTRY * (directory - DIRECTORY_BASE)
    place, file_number = fnt + _number(rom, entry), _number(rom, entry + FIELD_SIZE, SHORT_SIZE)
    found: list[tuple[str, int, bool]] = []
    while rom[place]:
        size, is_directory = rom[place] & ~DIRECTORY_FLAG, bool(rom[place] & DIRECTORY_FLAG)
        name = rom[place + 1 : place + 1 + size].decode("latin1")
        place += 1 + size
        if is_directory:
            found = [*found, (name, _number(rom, place, SHORT_SIZE), True)]
            place += SHORT_SIZE
        else:
            found = [*found, (name, file_number, False)]
            file_number += 1
    return found


def _walk(rom: bytes, directory: int, path: Path) -> list[tuple[Path, int]]:
    """Every file under a directory with its number, depth first, in listing order."""
    if len(path) > MAX_DEPTH:
        return []
    files: list[tuple[Path, int]] = []
    for name, number, is_directory in _listing(rom, directory):
        files = files + (
            _walk(rom, number, (*path, name)) if is_directory else [((*path, name), number)]
        )
    return files


def files(rom: bytes) -> tuple[tuple[Path, int], ...]:
    """Every file the cartridge carries, by path, with its number."""
    return tuple(_walk(rom, DIRECTORY_BASE, ()))


def read_file(rom: bytes, path: Path) -> bytes:
    """One file's bytes, found by its path."""
    number = next((found for name, found in files(rom) if name == path), None)
    if number is None:
        message = f"the cartridge carries no file {'/'.join(path)}"
        raise KeyError(message)
    entry = _number(rom, FAT_OFFSET_FIELD) + FAT_ENTRY * number
    return rom[_number(rom, entry) : _number(rom, entry + FIELD_SIZE)]
