"""The devices a card can be made for, each with its own way of reading a barcode."""

from enum import StrEnum
from typing import Final


class Device(StrEnum):
    """One reader. The value is the short key the command line and the page use."""

    BB2 = "bb2"
    BB1 = "bb1"
    DOUBLE = "double"
    DATACH_DBZ = "dbz"
    DATACH_ULTRAMAN = "ultraman"
    DATACH_SD_GUNDAM = "sdgundam"
    DATACH_YUYU = "yuyu"
    DATACH_JLEAGUE = "jleague"
    DATACH_BATTLE_RUSH = "battlerush"
    BARCODE_WORLD = "barcodeworld"
    SENKI = "senki"
    LUPIN = "lupin"
    DONALD = "donald"
    SPIDERMAN = "spiderman"
    ALICE = "alice"
    DORAEMON2 = "doraemon2"
    DORAEMON3 = "doraemon3"
    YOUSEI = "yousei"
    EXCITE95 = "excite95"
    DSLAYER2 = "dslayer2"
    HATAYAMA = "hatayama"
    EXCITE94 = "excite94"
    BATTLE_SPACE = "bspace"
    MONSTER_MAKER = "monstmkb"

    @property
    def is_game(self) -> bool:
        """Whether this is a game with a barcode reader rather than a standalone machine."""
        return self not in _MACHINES

    @property
    def english(self) -> str:
        """The device's name in English."""
        return _NAMES[self][0]

    @property
    def japanese(self) -> str:
        """The device's name in Japanese, as its maker printed it."""
        return _NAMES[self][1]


_MACHINES: Final = frozenset({Device.BB2, Device.BB1, Device.DOUBLE})

_NAMES: Final[dict[Device, tuple[str, str]]] = {
    Device.BB2: ("Barcode Battler 2", "バーコードバトラー2"),
    Device.BB1: ("Barcode Battler", "バーコードバトラー"),
    Device.DOUBLE: ("Barcode Battler 2 Double", "バーコードバトラー2 ダブル"),
    Device.DATACH_DBZ: ("Datach Dragon Ball Z", "データック ドラゴンボールZ"),
    Device.DATACH_ULTRAMAN: ("Datach Ultraman Club", "データック ウルトラマン倶楽部"),
    Device.DATACH_SD_GUNDAM: ("Datach SD Gundam Wars", "データック SDガンダム ガンダムウォーズ"),
    Device.DATACH_YUYU: ("Datach Yu Yu Hakusho", "データック 幽遊白書"),
    Device.DATACH_JLEAGUE: ("Datach J.League", "データック Jリーグ スーパートッププレイヤーズ"),
    Device.DATACH_BATTLE_RUSH: ("Datach Battle Rush", "データック バトルラッシュ"),
    Device.BARCODE_WORLD: ("Barcode World", "バーコードワールド"),
    Device.SENKI: ("Barcode Battler Senki", "バーコードバトラー戦記"),
    Device.LUPIN: ("Lupin III", "ルパン三世 伝説の秘宝を追え!"),
    Device.DONALD: ("Donald Duck no Mahou no Boushi", "ドナルドダックの魔法のぼうし"),
    Device.SPIDERMAN: ("Spider-Man: Lethal Foes", "スパイダーマン リーサルフォーズ"),
    Device.ALICE: ("Alice no Paint Adventure", "アリスのペイントアドベンチャー"),
    Device.DORAEMON2: ("Doraemon 2", "ドラえもん2 のび太のトイズランド大冒険"),
    Device.DORAEMON3: ("Doraemon 3", "ドラえもん3 のび太と時の宝玉"),
    Device.YOUSEI: ("Doraemon: Yousei no Kuni", "ドラえもん のび太と妖精の国"),
    Device.EXCITE95: ("J.League Excite Stage '95", "J.リーグエキサイトステージ'95"),
    Device.DSLAYER2: ("Dragon Slayer II", "ドラゴンスレイヤー英雄伝説II"),
    Device.HATAYAMA: ("Hatayama Hatch", "はた山ハッチのパロ野球ニュース!実名版"),
    Device.EXCITE94: ("J.League Excite Stage '94", "J.リーグエキサイトステージ'94"),
    Device.BATTLE_SPACE: ("Battle Space", "バトルスペース"),
    Device.MONSTER_MAKER: ("Monster Maker: Barcode Saga", "モンスターメーカー バーコードサーガ"),
}
