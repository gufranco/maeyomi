"""Cards Epoch released, as the community has transcribed them.

Epoch never published a machine-readable card list. What exists is the set of
pages on wikiwiki.jp where collectors typed in the barcode printed on each card
they own. That is the source here, fetched on the date recorded in `cards.json`
and kept with the address of the page every entry came from, so any one of
them can be checked again.

Two limits follow from the source and are kept visible rather than smoothed
over:

- A transcription can be wrong. Five entries carry a check digit that does not
  match their other twelve digits, which means somebody mistyped a digit. The
  wrong digit cannot be identified, so those five are rejected and listed by
  `rejected_transcriptions`, never repaired by guessing.
- A card missing from every page is missing here. The catalogue is the known
  cards, not a proof that no others were printed.

Each card is decoded by this project's own decoder before it is offered for
printing, so the numbers on the printed face come from the barcode rather than
from the transcription. Each list is read by the device its ability wording
belongs to: four lists use the first Barcode Battler's flag table, where 05
doubles the attack and 18 is the hero; 正伝3 破壊神伝 was bundled with the
Barcode Battler II Double and needs its 7-read; the rest use the Barcode
Battler II's.
"""

import json
from dataclasses import dataclass
from enum import Enum
from functools import cache
from importlib import resources
from typing import Final

from maeyomi.bb1.decode import decode_first
from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import BarcodeError
from maeyomi.double.decode import decode_double
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, GeneratedCard

DATA_FILE: Final = "cards.json"


class OfficialSet(Enum):
    """One card list, named as the wiki names it, with an English title.

    The English titles are this project's own translation, for readers who do
    not read Japanese. The Japanese value is what the source says.
    """

    ORIGINAL = "バーコードバトラー カードリスト"
    SECOND = "バーコードバトラーⅡ カードリスト"
    BOARD_GAME = "バーコードバトラーⅡ ボードゲーム付属カードリスト"
    STRONGEST_BATTLERS = "最強バトラー烈伝 カードリスト"
    CONVENIENCE_STORE_ONE = "コンビニ武闘伝第1弾 カードリスト"
    CONVENIENCE_STORE_TWO = "コンビニ武闘伝第2弾 カードリスト"
    GOD_VERSUS_MOTHER = "最後の決戦ゴッドＶＳマザー カードリスト"
    CHUHAI_KHAN = "チューハイカーンの逆襲 カードリスト"
    BARCODE_EMPEROR = "バーコード皇帝からの挑戦状 カードリスト"
    SIDE_STORY_ONE = "外伝1 白魔術王ホカロンダーの陰謀 カードリスト"
    SIDE_STORY_TWO = "外伝2 古魔術王グロンサンダーの復讐 カードリスト"
    SIDE_STORY_THREE = "外伝3 最後の死闘！ＶＳ黒魔術王パノラマンダー カードリスト"
    MAIN_STORY_THREE = "正伝3 破壊神伝 カードリスト"
    CANDY = "バーコードバトラーキャンデー カードリスト"

    @property
    def device(self) -> Device:
        """The device whose ability table this list's wording follows."""
        if self in _FIRST_DEVICE_SETS:
            return Device.BB1
        return Device.DOUBLE if self is OfficialSet.MAIN_STORY_THREE else Device.BB2

    @property
    def english(self) -> str:
        """A title a reader without Japanese can use."""
        return _ENGLISH_TITLES[self]


_FIRST_DEVICE_SETS: Final = frozenset(
    {
        OfficialSet.ORIGINAL,
        OfficialSet.CHUHAI_KHAN,
        OfficialSet.GOD_VERSUS_MOTHER,
        OfficialSet.CANDY,
    }
)

_ENGLISH_TITLES: Final[dict[OfficialSet, str]] = {
    OfficialSet.ORIGINAL: "Barcode Battler",
    OfficialSet.SECOND: "Barcode Battler II",
    OfficialSet.BOARD_GAME: "Barcode Battler II board game",
    OfficialSet.STRONGEST_BATTLERS: "Legends of the Strongest Battlers",
    OfficialSet.CONVENIENCE_STORE_ONE: "Convenience Store Fighters, series 1",
    OfficialSet.CONVENIENCE_STORE_TWO: "Convenience Store Fighters, series 2",
    OfficialSet.GOD_VERSUS_MOTHER: "The Final Battle: God versus Mother",
    OfficialSet.CHUHAI_KHAN: "Chuhai Khan Strikes Back",
    OfficialSet.BARCODE_EMPEROR: "A Challenge from the Barcode Emperor",
    OfficialSet.SIDE_STORY_ONE: "Side Story 1: The White Sorcerer King's Plot",
    OfficialSet.SIDE_STORY_TWO: "Side Story 2: The Ancient Sorcerer King's Revenge",
    OfficialSet.SIDE_STORY_THREE: "Side Story 3: The Last Duel with the Black Sorcerer King",
    OfficialSet.MAIN_STORY_THREE: "Main Story 3: Legend of the God of Destruction",
    OfficialSet.CANDY: "Barcode Battler candy",
}


@dataclass(frozen=True, slots=True)
class OfficialCard:
    """One transcribed card and where it was read from."""

    barcode: str
    name: str
    official_set: OfficialSet
    source_url: str


@cache
def official_catalogue() -> tuple[OfficialCard, ...]:
    """Every transcribed card, valid or not, in set order."""
    raw = resources.files("maeyomi.official").joinpath(DATA_FILE).read_text("utf-8")
    entries = json.loads(raw)["cards"]
    return tuple(
        OfficialCard(
            barcode=entry["barcode"],
            name=entry["name"],
            official_set=OfficialSet(entry["set"]),
            source_url=entry["source_url"],
        )
        for entry in entries
    )


def official_cards(official_set: OfficialSet | None = None) -> tuple[AnyCard, ...]:
    """Every card that decodes, optionally from one set, read by the device it was made for."""
    return tuple(
        _card(entry)
        for entry in official_catalogue()
        if (official_set is None or entry.official_set is official_set) and _decodes(entry)
    )


def _card(entry: OfficialCard) -> AnyCard:
    """Decode one card with its own device's reading."""
    device = entry.official_set.device
    if device is Device.BB1:
        return GeneratedCard(
            name=entry.name, barcode=entry.barcode, character=decode_first(entry.barcode)
        )
    if device is Device.DOUBLE:
        return GeneratedCard(
            name=entry.name, barcode=entry.barcode, character=decode_double(entry.barcode)
        )
    return GeneratedCard(name=entry.name, barcode=entry.barcode, character=decode(entry.barcode))


def rejected_transcriptions() -> tuple[OfficialCard, ...]:
    """Every transcription the decoder refuses, so a reader can see what was left out."""
    return tuple(entry for entry in official_catalogue() if not _decodes(entry))


def _decodes(entry: OfficialCard) -> bool:
    """Whether the transcribed barcode is one the device would accept."""
    try:
        decode(entry.barcode)
    except BarcodeError:
        return False
    return True
