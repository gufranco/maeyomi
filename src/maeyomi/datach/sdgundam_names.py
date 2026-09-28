"""What Datach SD Gundam Wars calls its units, weapons and command cards.

The Japanese names, model numbers, weapon names and command wording are the
game's own, copied off its barcode lab screen for a code of every unit, every
weapon and every command, run in MAME. Model numbers are kept as the lab prints
them, even where the series numbers a suit differently. The English is the
name the Gundam series uses in English, or this project's translation.

A command card is numbered 101 and up, the number the game's slot table gives
it, so one number names any card.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.datach.sdgundam_tables import COMMAND_COSTS, FIRST_COMMAND


@dataclass(frozen=True, slots=True)
class Unit:
    """A mobile suit: its model number and its name in both languages."""

    model: str
    english: str
    japanese: str


@dataclass(frozen=True, slots=True)
class Command:
    """A command card: its name, what it does, and the CP it costs."""

    english: str
    japanese: str
    effect: str
    effect_japanese: str
    cost: int


UNITS: Final[dict[int, Unit]] = {
    0: Unit("RX-78", "Gundam", "ガンダム"),
    1: Unit("RX-78NT1", "Alex", "アレックス"),
    2: Unit("RX78GP01", "Gundam GP01", "ガンダムGP01"),
    3: Unit("RX78GP02", "Gundam GP02", "ガンダムGP02"),
    4: Unit("RX78GP03", "Gundam GP03", "ガンダムGP03"),
    5: Unit("RGM-79N", "GM Custom", "ジムカスタム"),
    6: Unit("RGC-83", "GM Cannon II", "ジムキャノンII"),
    7: Unit("MSZ-006", "Zeta Gundam", "Zガンダム"),
    8: Unit("RMS-099", "Rick Dias", "リック・ディアス"),
    9: Unit("MS-14S", "Char's Gelgoog", "シャアゲルググ"),
    10: Unit("MSZ-010", "ZZ Gundam", "ZZガンダム"),
    11: Unit("RX-93", "Nu Gundam", "νガンダム"),
    12: Unit("RGZ-91", "Re-GZ", "リ・ガズィ"),
    13: Unit("F91", "Gundam F91", "ガンダムF91"),
    14: Unit("MS-05", "Zaku I", "ザクI"),
    15: Unit("MS-06F", "Zaku II", "ザクII"),
    16: Unit("MS-09", "Dom", "ドム"),
    17: Unit("MS-14A", "Gelgoog", "ゲルググ"),
    18: Unit("MSN-02", "Zeong", "ジオング"),
    19: Unit("MS-18E", "Kampfer", "ケンプファー"),
    20: Unit("MS-07B", "Gouf", "グフ"),
    21: Unit("MSM-07", "Z'Gok", "ズゴック"),
    22: Unit("MS-18E", "Gerbera Tetra", "ガーベラ・テトラ"),
    23: Unit("MS-21C", "Dra-C", "ドラッツェ"),
    24: Unit("RMS-106", "Hizack", "ハイザック"),
    25: Unit("PMX-000", "Messala", "メッサーラ"),
    26: Unit("ORX-005", "Gaplant", "ギャプラン"),
    27: Unit("PMX-001", "Palace Athene", "パラス・アテネ"),
    28: Unit("AMX-004", "Qubeley", "キュベレイ"),
    29: Unit("NZ-000", "Quin Mantha", "クイン・マンサ"),
    30: Unit("AMX-109", "Capule", "カプール"),
    31: Unit("RX-139", "Hambrabi", "ハンブラビ"),
    32: Unit("AMX-009", "Dreissen", "ドライセン"),
    33: Unit("XM-05B", "Berga Balus", "ベルガ・バルス"),
    34: Unit("MSN-03", "Jagd Doga", "ヤクト・ドーガ"),
    35: Unit("AMS-119", "Sazabi", "サザビー"),
    36: Unit("AMS-119", "Geara Doga", "ギラ・ドーガ"),
    37: Unit("XM-05", "Berga Giros", "ベルガ・ギロス"),
    38: Unit("XM-07", "Vigna Ghina", "ビギナ・ギナ"),
    39: Unit("XM-01", "Denan Zon", "デナン・ゾン"),
    40: Unit("RX-178", "Gundam Mk-II", "ガンダムMkII"),
    41: Unit("RX-178", "Gundam Mk-II, black", "ガンダムMkII"),
    42: Unit("XM-01", "Denan Zon DT", "DTデナン・ゾン"),
    43: Unit("MSN-100", "Hyaku Shiki", "ヒャクシキ"),
    44: Unit("XM-04", "Berga Dalas", "ベルガ・ダラス"),
    45: Unit("RX-99", "Neo Gundam", "ネオガンダム"),
    46: Unit("RXF91", "RXF91", "RXF91"),
    47: Unit("MS-06S", "Char's Zaku", "シャアザク"),
    48: Unit("MSM-07S", "Char's Z'Gok", "シャアズゴック"),
    49: Unit("MAN-08", "Elmeth", "エルメス"),
    50: Unit("MS-15", "Gyan", "ギャン"),
    51: Unit("NRX-044", "Asshimar", "アッシマー"),
    52: Unit("RMS-177", "Galbaldy Beta", "ガルバルディβ"),
    53: Unit("RMS-108", "Marasai", "マラサイ"),
    54: Unit("PMX-003", "The O", "ジ・オ"),
    55: Unit("AMX-003", "Gaza-C", "ガザC"),
    56: Unit("AMX-103", "Hamma Hamma", "ハンマ・ハンマ"),
    57: Unit("AMX-101", "Galluss-J", "ガルスJ"),
    58: Unit("XM-02", "Denan Gei", "デナン・ゲー"),
    59: Unit("AMX-107", "Bawoo", "バウ"),
    60: Unit("AMX-110", "Zaku III", "ザクIII"),
    61: Unit("AMX-014", "Doven Wolf", "ドーベン・ウルフ"),
    62: Unit("AMX-004G", "Mass-production Qubeley", "りょうキュベレイ"),
}

WEAPONS: Final[dict[int, tuple[str, str]]] = {
    0: ("Beam saber", "ビームサーベル"),
    1: ("Vulcan", "バルカン"),
    2: ("Heat hawk", "ヒートホーク"),
    3: ("Beam tomahawk", "ビームトマホーク"),
    4: ("Beam rifle", "ビームライフル"),
    5: ("Bazooka", "バズーカ"),
    6: ("Funnels", "ファンネル"),
    7: ("Missiles", "ミサイル"),
    8: ("Machine gun", "マシンガン"),
    9: ("Shot lancer", "ショットランサー"),
    10: ("Beam machine gun", "ビームマシンガン"),
    11: ("Beam gun", "ビームほう"),
    12: ("Claw", "クロー"),
    13: ("Heat rod", "ヒートロッド"),
    14: ("Hand vulcan", "ハンドバルカン"),
    15: ("Vulcan", "バルカン"),
    16: ("Arm punch", "アームパンチ"),
    17: ("Mega particle cannon", "メガりゅうしほう"),
    18: ("Beam cannon", "ビームキャノン"),
    19: ("High mega cannon", "ハイメガキャノン"),
    20: ("VSBR", "ヴェスバー"),
    21: ("Hand cannon", "ハンドキャノン"),
    22: ("Mega particle cannon", "メガりゅうしほう"),
    23: ("Beam gun", "ビームほう"),
}

_COMMANDS: Final[dict[int, tuple[str, str, str, str]]] = {
    1: (
        "Everyone charge!",
        "みんなつっこめ",
        "Each unit makes a close attack on one enemy of its own.",
        "それぞれが 1たい1の せっきんコウゲキを します",
    ),
    2: (
        "Please go!",
        "たのむいってくれ",
        "The unit with the least HP guards; the others make close attacks.",
        "HPの いちばん ひくい MSは ボウギョ ほかの MSは せっきんコウゲキを します",
    ),
    3: (
        "I'll go!",
        "オレがいく",
        "The unit with the most HP makes a close attack; the others guard.",
        "HPの いちばん たかい MSは せっきんコウゲキ ほかの MSは ボウギョ します",
    ),
    4: (
        "Everyone fire!",
        "みんなうて",
        "Each unit makes a ranged attack on one enemy of its own.",
        "それぞれが 1たい1の えんきょりコウゲキを します",
    ),
    5: (
        "Please fire!",
        "たのむうってくれ",
        "The unit with the least HP guards; the others make ranged attacks.",
        "HPの いちばん ひくい MSは ボウギョ ほかの MSは えんきょりコウゲキを します",
    ),
    6: (
        "I'll fire!",
        "オレがうつ",
        "The unit with the most HP makes a ranged attack; the others guard.",
        "HPの いちばん たかい MSは えんきょりコウゲキ ほかの MSは ボウギョ します",
    ),
    7: (
        "Cut down the ace!",
        "エースをきれ",
        "Every unit makes a close attack on the enemy with the most HP.",
        "いちばん HPの たかい MSに しゅうちゅうして ちょくせつコウゲキを します",
    ),
    8: (
        "Scatter the small fry!",
        "ザコをけちらせ",
        "Every unit makes a close attack on the enemy with the least HP.",
        "いちばん HPの ひくい MSに しゅうちゅうして ちょくせつコウゲキを します",
    ),
    9: (
        "Aim for the ace!",
        "エースをねらえ",
        "Every unit makes a ranged attack on the enemy with the most HP.",
        "いちばん HPの たかい MSに しゅうちゅうして えんきょりコウゲキを します",
    ),
    10: (
        "Aim for the small fry!",
        "ザコをねらえ",
        "Every unit makes a ranged attack on the enemy with the least HP.",
        "いちばん HPの ひくい MSに しゅうちゅうして えんきょりコウゲキを します",
    ),
    11: (
        "Head-on fight!",
        "まっこうしょうぶ",
        "A ranged attack on the whole enemy force.",
        "てきぜんたいに たいし えんきょりコウゲキを します",
    ),
    12: (
        "Everyone rush!",
        "みんなとっしん",
        "A close attack on the whole enemy force.",
        "てきぜんたいに たいし ちょくせつコウゲキを します",
    ),
    13: (
        "Strike first!",
        "さきにやっちまえ",
        "Takes the first move against the enemy force and makes a ranged attack.",
        "テキぜんたいに たいし せんてを とって えんきょりコウゲキを します",
    ),
    14: (
        "First strike wins!",
        "せんてひっしょう",
        "Takes the first move against the enemy force and makes a close attack.",
        "テキぜんたいに たいし せんてを とって ちょくせつコウゲキを します",
    ),
    15: (
        "Hold the line!",
        "まもりをかためろ",
        "The whole force takes a defensive stance.",
        "ぜんたい ぼうぎょたいせいに はいります",
    ),
    17: (
        "La Vie en Rose",
        "ラビアンローズ",
        "La Vie en Rose appears and restores 70 percent of HP.",
        "ラビアンローズが あらわれて HPを 70パーセント かいふくします",
    ),
    18: (
        "White Base",
        "ホワイトベース",
        "White Base appears and restores 50 percent of HP.",
        "ホワイトベースが あらわれて HPを 50パーセント かいふくします",
    ),
    19: (
        "Medea",
        "ミデア",
        "A Medea appears and restores 30 percent of HP.",
        "ミデアが あらわれて HPを 30パーセント かいふくします",
    ),
    20: (
        "Gunperry",
        "ガンペリー",
        "A Gunperry appears and replaces one destroyed unit.",
        "ガンペリーが あらわれて はかいされた MSを 1き ほじゅう します",
    ),
    21: (
        "Mega Bazooka Launcher",
        "メガバズーカランチャー",
        "Fires the Mega Bazooka Launcher: heavy damage to the enemy force.",
        "メガバズーカランチャーで コウゲキし テキぜんたいに だいダメージを あたえます",
    ),
    22: (
        "Core Booster",
        "コアブースター",
        "Covering fire from a Core Booster: medium damage to the enemy force.",
        "コアブースターの えんごしゃげきで テキぜんたいに ちゅうダメージを あたえます",
    ),
    23: (
        "Combat satellite",
        "セントウえいせい",
        "Covering fire from a combat satellite: medium damage to the enemy force.",
        "セントウえいせいの えんごしゃげきで テキぜんたいに ちゅうダメージを あたえます",
    ),
    24: (
        "Gaw bombing",
        "ガウばくげき",
        "The Gaw bombs the enemy: medium damage to the whole force.",
        "ガウの ばくげきにより テキぜんたいに ちゅうダメージを あたえます",
    ),
    25: (
        "Mad Angler",
        "マッドアングラー",
        "Covering fire from the Mad Angler: medium damage to the enemy force.",
        "マッドアングラーの えんごしゃげきで テキぜんたいに ちゅうダメージを あたえます",
    ),
    26: (
        "Covering missiles",
        "えんごミサイル",
        "White Base's covering missiles: light damage to the enemy force.",
        "ホワイトベースの えんごミサイルで テキぜんたいに しょうダメージを あたえます",
    ),
    27: (
        "Nuclear missile",
        "かくミサイル",
        "Fires a nuclear missile: very heavy damage to the enemy force.",
        "かくミサイルを はっしゃして テキぜんたいに とくだいのダメージを あたえます",
    ),
    28: (
        "Lay down a barrage!",
        "ダンマクをはれ",
        "White Base's anti-air fire: light damage to the enemy force.",
        "ホワイトベースの かんぽうしゃげきで テキぜんたいに しょうダメージを あたえます",
    ),
    29: (
        "Fleet cover",
        "かんたいえんご",
        "The fleet's anti-air fire: medium damage to the enemy force.",
        "かんたいの かんぽうしゃげきで テキぜんたいに ちゅうダメージを あたえます",
    ),
    30: (
        "Dolos",
        "ドロス",
        "Covering fire from the Dolos: heavy damage to the enemy force.",
        "ドロスの えんごしゃげきで テキぜんたいに だいダメージを あたえます",
    ),
    31: (
        "Sieg Zeon",
        "ジーク・ジオン",
        "A Gaw rams the enemy: heavy damage to the whole force.",
        "ガウが テキに たいあたりをして テキぜんたいに だいダメージを あたえます",
    ),
    32: (
        "It's all right",
        "だいじょうぶ",
        "A Core Fighter rams one enemy for heavy damage.",
        "コアファイターが とっこうして テキ1きに だいダメージを あたえます",
    ),
    33: (
        "Jet Stream",
        "ジェットストリーム",
        "A Jet Stream Attack on one enemy.",
        "ジェットストリームアタックで テキ1きを コウゲキします",
    ),
    34: (
        "Ramming",
        "とっこう",
        "Rams one enemy with everything it has for heavy damage.",
        "テキに たいあたりをする すてみの コウゲキで だいダメージを あたえます",
    ),
    35: (
        "Colony Laser",
        "コロニーレーザー",
        "Zeon's colony laser: very heavy damage to the enemy force.",
        "ジオンの コロニーレーザーで テキぜんたいを コウゲキし とくだいのダメージを あたえます",
    ),
    36: (
        "Solar System",
        "ソーラーシステム",
        "The Federation's Solar System: very heavy damage to the enemy force.",
        "レンポウの ソーラーシステムで テキぜんたいを コウゲキし とくだいのダメージを あたえます",
    ),
    37: (
        "Colony drop",
        "コロニーおとし",
        "Drops a colony: very heavy damage to the enemy force.",
        "コロニーを らっかさせて テキぜんたいに とくだいのダメージを あたえます",
    ),
    38: (
        "Meteor drop",
        "インセキおとし",
        "Drops a meteor: very heavy damage to the enemy force.",
        "インセキを らっかさせて テキぜんたいに とくだいのダメージを あたえます",
    ),
    39: (
        "Big Zam",
        "ビグザム",
        "Big Zam's mega particle cannon: medium damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    40: (
        "Big Zam, diffuse",
        "ビグザム",
        "Big Zam's diffuse mega particle cannon: light damage to the enemy force.",
        "かくさんメガりゅうしほうで テキぜんたいを コウゲキし しょうダメージを あたえます",
    ),
    41: (
        "Val Walo",
        "ヴァル・ヴァロ",
        "Val Walo's mega particle cannon: medium damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    42: (
        "Val Walo, plasma",
        "ヴァル・ヴァロ",
        "Val Walo's plasma leader: medium damage to the enemy force.",
        "プラズマリーダーの でんげきで テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    43: (
        "Neue Ziel",
        "ノイエ・ジール",
        "Neue Ziel's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    44: (
        "Neue Ziel, diffuse",
        "ノイエ・ジール",
        "Neue Ziel's diffuse mega particle cannon: light damage to the enemy force.",
        "かくさんメガりゅうしほうで テキぜんたいを コウゲキし しょうダメージを あたえます",
    ),
    45: (
        "Dendrobium",
        "デンドロビウム",
        "Dendrobium's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    46: (
        "Dendrobium, arsenal",
        "デンドロビウム",
        "Dendrobium's weapon containers: medium damage to the enemy force.",
        "テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    47: (
        "Alpha Azieru",
        "α・アジール",
        "Alpha Azieru's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    48: (
        "Alpha Azieru, funnels",
        "α・アジール",
        "Alpha Azieru launches funnels: medium damage to the enemy force.",
        "ファンネルを ほうしゅつして テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    49: (
        "Rafflesia, diffuse",
        "ラフレシア",
        "Rafflesia's diffuse mega particle cannon: medium damage to the enemy force.",
        "かくさんメガりゅうしほうで テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    50: (
        "Rafflesia",
        "ラフレシア",
        "Rafflesia's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    51: (
        "Psyco Gundam, diffuse",
        "サイコガンダム",
        "Psyco Gundam's diffuse mega particle cannon: light damage to the enemy force.",
        "かくさんメガりゅうしほうで テキぜんたいを コウゲキし しょうダメージを あたえます",
    ),
    52: (
        "Psyco Gundam",
        "サイコガンダム",
        "Psyco Gundam's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    53: (
        "Psyco Gundam Mk-II",
        "サイコガンダムMkII",
        "Psyco Gundam Mk-II's mega particle cannon: heavy damage to the enemy force.",
        "メガりゅうしほうで テキぜんたいを コウゲキし だいダメージを あたえます",
    ),
    54: (
        "Psyco Gundam Mk-II, diffuse",
        "サイコガンダムMkII",
        "Psyco Gundam Mk-II's diffuse mega particle cannon: medium damage to the enemy force.",
        "かくさんメガりゅうしほうで テキぜんたいを コウゲキし ちゅうダメージを あたえます",
    ),
    55: (
        "Blinding flash",
        "めくらまし",
        "Dazzles the enemy and lowers how often its attacks hit.",
        "テキのめを くらまして コウゲキの めいちゅうりつを さげます",
    ),
    56: (
        "Magnet coating",
        "マグネットコーティング",
        "Raises speed, so the first move comes more easily.",
        "マグネットコーティングすることで スピードがまし せんてを とりやすく なります",
    ),
    57: (
        "Propellant tank",
        "プロペラントタンク",
        "Fits a propellant tank and raises the most HP a unit can have.",
        "プロペラントタンクを そうちゃくして HPの さいだいちを あげます",
    ),
    58: (
        "Full Armor Unit",
        "フルアーマーユニット",
        "Fits the Full Armor Unit and raises DP.",
        "フルアーマーユニットを そうちゃくして DPを あげます",
    ),
    59: (
        "Psycho-frame",
        "サイコフレーム",
        "The psycho-frame's mysterious power raises AP.",
        "サイコフレームの ふしぎなちからで APを あげます",
    ),
    60: (
        "Birdlime",
        "トリモチ",
        "A birdlime shot from a unit slows the enemy's movement.",
        "MSから はっしゃされた トリモチで テキMSの うごきを にぶくします",
    ),
}

COMMANDS: Final[dict[int, Command]] = {
    number: Command(*text, cost=COMMAND_COSTS[number]) for number, text in _COMMANDS.items()
}


def command_number(ident: int) -> int:
    """The command a card number names: 101 is command 1."""
    return ident - FIRST_COMMAND + 1


def card_named(typed: str) -> int:
    """The card a typed name, model number or card number means, or a ValueError."""
    wanted = typed.strip()
    folded = wanted.casefold()
    if wanted.isdigit() and (int(wanted) in UNITS or command_number(int(wanted)) in COMMANDS):
        return int(wanted)
    for ident, unit in UNITS.items():
        if folded in {unit.english.casefold(), unit.model.casefold(), unit.japanese}:
            return ident
    for number, command in COMMANDS.items():
        if folded in {command.english.casefold(), command.japanese}:
            return number + FIRST_COMMAND - 1
    message = f"unknown SD Gundam Wars card {typed!r}; name a unit, a model number or a command"
    raise ValueError(message)
