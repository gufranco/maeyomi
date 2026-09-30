"""Tests for the romaniser that gives every kana name the games show an English form."""

import unicodedata

import pytest

from maeyomi.romaji import romanised


@pytest.mark.parametrize(
    ("japanese", "english"),
    [
        ("フォワールド", "Fowaarudo"),
        ("ガウディ", "Gaudi"),
        ("ミイラターボ", "Miirataabo"),
        ("ビデオRXR", "Bideo RXR"),
        ("ABZ-11", "ABZ-11"),
        ("パックマンカー", "Pakkumankaa"),
        ("マッチ", "Matchi"),
        ("シェリーサボレ", "Sheriisabore"),
        ("ヴィナ", "Vina"),
        ("キャラメル", "Kyarameru"),
        ("ァ", "A"),
    ],
)
def test_katakana_is_romanised_by_rule(japanese: str, english: str) -> None:
    assert romanised(japanese) == english


@pytest.mark.parametrize(
    ("japanese", "english"),
    [
        ("ギャムVRー4", "Gyamu VR-4"),
        ("シェリカGTーR", "Sherika GT-R"),
        ("MISSー9", "MISS-9"),
        ("コロリXーEVE", "Korori X-EVE"),
    ],
)
def test_a_long_mark_between_letters_is_a_hyphen(japanese: str, english: str) -> None:
    assert romanised(japanese) == english


@pytest.mark.parametrize(
    ("japanese", "english"),
    [
        ("がまもと くにくに", "Gamamoto Kunikuni"),
        ("ディド ハーフナー", "Dido Haafunaa"),
        ("しょうじ よなひろ", "Shouji Yonahiro"),
        ("はじしま のぶろう", "Hajishima Noburou"),
        ("あいのせんし ハタ3", "Ainosenshi Hata 3"),
    ],
)
def test_hiragana_names_keep_their_words(japanese: str, english: str) -> None:
    assert romanised(japanese) == english


@pytest.mark.parametrize(
    ("japanese", "english"),
    [
        ("Y・ミヤーン / ブロッコリィ", "Y Miyaan / Burokkori"),
        ("SID2800 / ゴーリキー", "SID2800 / Goorikii"),
        ("E・キヨハラ / きよひめS-3", "E Kiyohara / Kiyohime S-3"),
        ("ミスターX / ボンボンR-01", "Misutaa X / Bonbon R-01"),
    ],
)
def test_a_middle_dot_separates_words(japanese: str, english: str) -> None:
    assert romanised(japanese) == english


def test_no_kana_survives_any_name_the_games_show() -> None:
    kana = "".join(
        chr(point) for point in range(0x3041, 0x3100) if unicodedata.name(chr(point), "")
    )

    result = romanised(kana)

    assert not any("぀" <= character <= "ヿ" for character in result)
