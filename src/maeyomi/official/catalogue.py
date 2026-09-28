"""Cards Epoch released, as the community has transcribed them.

Epoch never published a machine-readable card list. What exists is the set of
pages on wikiwiki.jp where collectors typed in the barcode printed on each card
they own. That is the source here, fetched on the date recorded in `cards.json`
and kept with the address of the page every entry came from, so any one of
them can be checked again. The 36 cards Bandai packed with Datach Dragon Ball Z
come from the list in the puNES emulator's source instead, and each was read by
the game itself running in MAME before it was added. The 38 Ultraman Club cards
are the codes retrostuff.org read off the cards in its own set, named as the
puNES list names them, and each was read by the game in MAME as well. The Zelda, Shogaku
Ninensei and Street Fighter II cards come from the card lists in
barcodebattler.co.uk's deeta.js, a collector site that publishes them in
English; one Zelda item, the red potion, is also a card of the board game list.
The Dragon Slayer, Doraemon, Obocchama-kun and Meiji cards were read off the card
scans barcodebattler.co.uk publishes, one barcode per card cell, and each is tied
to its name by the numbers printed on the card's front. Only two of the Meiji
cards, numbered 1 and 5, have been scanned. The Obocchama-kun cards say they work
with the Barcode Battler, not the II, so they print with the first device.

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
from the transcription. Each list is read by the device it was written for:
five lists use the first Barcode Battler's flag table, where 05 doubles the
attack and 18 is the hero; 正伝3 and 正伝4 need the Barcode Battler II Double's
7-read, which half of 正伝4's cards use; the Dragon Ball Z list is read the way
that game reads it; the rest use the Barcode Battler II's. The God Mars list
publishes no numbers, so its device comes from its cards: it has no magician
and no herb or magic item, both of which only the II reads, and it sits among
the first Barcode Battler's lists in the collector site's series.
"""

import json
from dataclasses import dataclass
from enum import Enum
from functools import cache
from importlib import resources
from typing import Final

from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard
from maeyomi.registry import printable_as

DATA_FILE: Final = "cards.json"


class OfficialSet(Enum):
    """One card list, with its Japanese and English titles.

    The English titles are this project's own translation, for readers who do
    not read Japanese. The Japanese value is the wiki's page name, and for the
    three lists published in English it is this project's translation.
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
    GOD_MARS = "魔強軍団ゴッドマーズ出現！ カードリスト"
    MAIN_STORY_ONE = "正伝1 超パワー生命体！ダークバーコード星人登場！！ カードリスト"
    MAIN_STORY_TWO = "正伝2 超合体伝説 カードリスト"
    MAIN_STORY_FOUR = "正伝4 精霊伝説 カードリスト"
    MACHINE_DRAGONS = "来襲！機械竜軍団！！ カードリスト"
    ZELDA = "ゼルダの伝説 カードリスト"
    SECOND_GRADE = "小学二年生 特製カードリスト"
    STREET_FIGHTER = "ストリートファイターII カードリスト"
    DRAGON_SLAYER = "ドラゴンスレイヤー英雄伝説 カードリスト"
    DORAEMON_DINOSAUR = "ドラえもん のび太の恐竜 カードリスト"
    OBOCCHAMAKUN = "おぼっちゃまくん ドラゴンバトラー カードリスト"
    MEIJI_FREEZELAND = "明治 フリーズランドの戦士達 カードリスト"
    DATACH_DBZ = "データック ドラゴンボールZ 激闘天下一武道会 カードリスト"
    DATACH_ULTRAMAN = "データック ウルトラマン倶楽部 スポ根ファイト! カードリスト"

    @property
    def device(self) -> Device:
        """The device whose ability table this list's wording follows."""
        return _DEVICES.get(self, Device.BB2)

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
        OfficialSet.GOD_MARS,
        OfficialSet.OBOCCHAMAKUN,
    }
)

_DEVICES: Final[dict[OfficialSet, Device]] = {
    **dict.fromkeys(_FIRST_DEVICE_SETS, Device.BB1),
    OfficialSet.MAIN_STORY_THREE: Device.DOUBLE,
    OfficialSet.MAIN_STORY_FOUR: Device.DOUBLE,
    OfficialSet.DATACH_DBZ: Device.DATACH_DBZ,
    OfficialSet.DATACH_ULTRAMAN: Device.DATACH_ULTRAMAN,
}

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
    OfficialSet.GOD_MARS: "The Demon Army God Mars Appears",
    OfficialSet.MAIN_STORY_ONE: "Main Story 1: The Super-Powered Dark Barcode Aliens Arrive",
    OfficialSet.MAIN_STORY_TWO: "Main Story 2: The Legend of Super Fusion",
    OfficialSet.MAIN_STORY_FOUR: "Main Story 4: The Legend of the Spirits",
    OfficialSet.MACHINE_DRAGONS: "The Machine Dragon Army Attacks",
    OfficialSet.ZELDA: "The Legend of Zelda",
    OfficialSet.SECOND_GRADE: "Shogaku Ninensei special cards",
    OfficialSet.STREET_FIGHTER: "Street Fighter II",
    OfficialSet.DRAGON_SLAYER: "Dragon Slayer: The Legend of Heroes",
    OfficialSet.DORAEMON_DINOSAUR: "Doraemon: Nobita's Dinosaur",
    OfficialSet.OBOCCHAMAKUN: "Obocchama-kun Dragon Battler",
    OfficialSet.MEIJI_FREEZELAND: "Meiji: The Warriors of Freezeland",
    OfficialSet.DATACH_DBZ: "Datach Dragon Ball Z: Gekitou Tenkaichi Budoukai",
    OfficialSet.DATACH_ULTRAMAN: "Datach Ultraman Club: Supokon Fight!",
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
    return printable_as(entry.official_set.device, entry.barcode, entry.name)


def sets_for(device: Device) -> tuple[OfficialSet, ...]:
    """The sets written for one device, in catalogue order."""
    return tuple(official_set for official_set in OfficialSet if official_set.device is device)


def device_cards(device: Device) -> tuple[AnyCard, ...]:
    """Every printable card of every set written for one device."""
    return tuple(card for official_set in sets_for(device) for card in official_cards(official_set))


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
