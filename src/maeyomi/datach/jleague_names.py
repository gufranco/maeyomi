"""The teams and players Datach J.League Super Top Players knows, in 1993's squads.

The Japanese names are the game's own, copied off its player directory,
せんしゅめいかん, for every barcode Bandai printed, run in MAME. The English
names follow the spreadsheet archive.org keeps beside its scans of the set,
with its clear misspellings corrected; that spreadsheet calls its own names of
debatable accuracy, so a name here is only as sure as that.

A card is numbered by team and shirt slot: team times 16, plus the player's
slot from 1 to 15, and 0 for the team's own card.
"""

from typing import Final

from maeyomi.said import Said

TEAM_SLOTS: Final = 16

TEAMS: Final[dict[int, tuple[str, str]]] = {
    0: ("Kashima Antlers", "鹿島アントラーズ"),
    1: ("East Japan JR Furukawa Soccer Club", "東日本JR古河サッカークラブ"),
    2: ("Mitsubishi Urawa Football Club", "三菱浦和フットボールクラブ"),
    3: ("Yomiuri Nippon Soccer Club", "読売日本サッカークラブ"),
    4: ("Nissan F.C. Yokohama Marinos", "日産F.C.横浜マリノス"),
    5: ("ANA Sato Kogyo Soccer Club", "全日空佐藤工業サッカークラブ"),
    6: ("Shimizu FC S-Pulse", "清水FCエスパルス"),
    7: ("Nagoya Grampus Eight", "名古屋グランパスエイト"),
    8: ("Panasonic Gamba Osaka", "パナソニックガンバ大阪"),
    9: ("Sanfrecce Hiroshima F.C.", "サンフレッチェ広島F.C."),
}

_SQUADS: Final[dict[int, tuple[tuple[str, str], ...]]] = {
    0: (
        ("Masaaki Furukawa", "古川 昌明"),
        ("Yutaka Akita", "秋田 豊"),
        ("Eiji Kaya", "賀谷 英司"),
        ("Makoto Sugiyama", "杉山 誠"),
        ("Shunzo Ono", "大野 俊三"),
        ("Yasuto Honda", "本田 泰人"),
        ("Alcindo", "アルシンド"),
        ("Santos", "サントス"),
        ("Hisashi Kurosaki", "黒崎 比差支"),
        ("Zico", "ジーコ"),
        ("Masatada Ishii", "石井 正忠"),
        ("Kazuhisa Irii", "入井 和久"),
        ("Satoshi Koga", "古賀 聡"),
        ("Yoshiyuki Hasegawa", "長谷川 祥之"),
        ("Yasuo Manaka", "真中 靖夫"),
    ),
    1: (
        ("Kenichi Shimokawa", "下川 健一"),
        ("Masanao Sasaki", "佐々木 雅尚"),
        ("Eisuke Nakanishi", "中西 永輔"),
        ("Yuji Sakakura", "阪倉 裕二"),
        ("Masanaga Kageyama", "影山 雅永"),
        ("Michel Miyazawa", "宮澤 ミッシェル"),
        ("Pavel", "パベル"),
        ("Kazuo Echigo", "越後 和男"),
        ("Otze", "オッツェ"),
        ("Pierre Littbarski", "リトバルスキー"),
        ("Atsuhiko Ejiri", "江尻 篤彦"),
        ("Hiroshi Miyazawa", "宮澤 浩"),
        ("Toru Yoshida", "吉田 暢"),
        ("Giichi Goto", "後藤 義一"),
        ("Keisuke Makino", "牧野 景輔"),
    ),
    2: (
        ("Milo", "ミロ"),
        ("Hiroyuki Sawada", "澤田 浩悠起"),
        ("Futoshi Ikeda", "池田 太"),
        ("Go Motoyoshi", "本吉 剛"),
        ("Satoshi Mochizuki", "望月 聡"),
        ("Osamu Hirose", "広瀬 治"),
        ("Uwe Rahn", "ラーン"),
        ("Atsushi Natori", "名取 篤"),
        ("Masahiro Fukuda", "福田 正博"),
        ("Michael Rummenigge", "ルムメニゲ"),
        ("Koichi Hashiratani", "柱谷 幸一"),
        ("Shinji Tanaka", "田中 真二"),
        ("Takashi Hori", "堀 孝史"),
        ("Takeshi Mizuuchi", "水内 猛"),
        ("Shinichi Kawano", "河野 真一"),
    ),
    3: (
        ("Shinkichi Kikuchi", "菊池 新吉"),
        ("Yasushi Ishikawa", "石川 康"),
        ("Pereira", "ペレイラ"),
        ("Rossum", "ロッサム"),
        ("Tetsuji Hashiratani", "柱谷 哲二"),
        ("Satoshi Tsunami", "都並 敏史"),
        ("Bismarck", "ビスマルク"),
        ("Tsuyoshi Kitazawa", "北澤 豪"),
        ("Nobuhiro Takeda", "武田 修宏"),
        ("Ruy Ramos", "ラモス 瑠偉"),
        ("Kazuyoshi Miura", "三浦 知良"),
        ("Shinji Fujiyoshi", "藤吉 信次"),
        ("Mitsuhiro Kawamoto", "河本 充弘"),
        ("Tetsuya Totsuka", "戸塚 哲也"),
        ("Hideki Nagai", "永井 秀樹"),
    ),
    4: (
        ("Shigetatsu Matsunaga", "松永 成立"),
        ("Hiroshi Hirakawa", "平川 弘"),
        ("Toshinobu Katsuya", "勝矢 寿延"),
        ("Masami Ihara", "井原 正巳"),
        ("Norio Omura", "小村 徳男"),
        ("Atsushi Koizumi", "小泉 淳嗣"),
        ("Everton", "エバートン"),
        ("Takashi Mizunuma", "水沼 貴史"),
        ("Diaz", "ディアス"),
        ("Kazushi Kimura", "木村 和司"),
        ("Visconti", "ビスコンティ"),
        ("Kunio Nagayama", "永山 邦夫"),
        ("Keiichi Zaizen", "財前 恵一"),
        ("Fumitake Miura", "三浦 文丈"),
        ("Takuya Jinno", "神野 卓哉"),
    ),
    5: (
        ("Atsuhiko Mori", "森 敦彦"),
        ("Naoto Otake", "大嶽 直人"),
        ("Ippei Watanabe", "渡辺 一平"),
        ("Atsuhiro Iwai", "岩井 厚裕"),
        ("Motohiro Yamaguchi", "山口 素弘"),
        ("Moner", "モネール"),
        ("Yasuharu Sorimachi", "反町 康治"),
        ("Masaaki Takada", "高田 昌明"),
        ("Osamu Maeda", "前田 治"),
        ("Edu M.", "エドゥーM"),
        ("Audro", "アウドロ"),
        ("Ryohiro Satsukawa", "薩川 了洋"),
        ("Ichizo Nakata", "中田 一三"),
        ("Hideki Katsura", "桂 秀樹"),
        ("Masakiyo Maezono", "前園 真聖"),
    ),
    6: (
        ("Sidmar", "シジマール"),
        ("Hisashi Kato", "加藤 久"),
        ("Gomez", "ゴメス"),
        ("Takumi Horiike", "堀池 巧"),
        ("Yasutoshi Miura", "三浦 泰年"),
        ("Hiroshi Saito", "斉藤 浩史"),
        ("Katsumi Oenoki", "大榎 克己"),
        ("Edu S.", "エドゥーS"),
        ("Kenta Hasegawa", "長谷川 健太"),
        ("Masaaki Sawanobori", "澤登 正朗"),
        ("Ken Mukojima", "向島 建"),
        ("Naoki Naito", "内藤 直樹"),
        ("Takamitsu Ota", "太田 貴光"),
        ("Masafumi Sugimoto", "杉本 雅央"),
        ("Hiroaki Tajima", "田島 宏晃"),
    ),
    7: (
        ("Yuji Ito", "伊藤 裕二"),
        ("Seiichi Ogawa", "小川 誠一"),
        ("Hisataka Fujikawa", "藤川 久孝"),
        ("Toshihisa Iijima", "飯島 寿久"),
        ("Garza", "ガルサ"),
        ("Michihiro Tsuruta", "鶴田 道弘"),
        ("Makoto Yonekura", "米倉 誠"),
        ("Tetsuya Asano", "浅野 哲也"),
        ("Jorginho", "ジョルジーニョ"),
        ("Gary Lineker", "リネカー"),
        ("Yasuyuki Moriyama", "森山 泰行"),
        ("Kei Taniguchi", "谷口 圭"),
        ("Tetsuya Okayama", "岡山 哲也"),
        ("Masashi Shimamura", "島村 征志"),
        ("Taro Goto", "後藤 太郎"),
    ),
    8: (
        ("Kenji Honnami", "本並 健治"),
        ("Jia Xiuquan", "賈 秀全"),
        ("Koji Imafuji", "今藤 幸治"),
        ("Tomoyuki Kajino", "梶野 智幸"),
        ("Tomoo Kudaka", "久高 友雄"),
        ("Masahiro Wada", "和田 昌裕"),
        ("Aleinikov", "アレイニコフ"),
        ("Metkov", "メトコフ"),
        ("Akihiro Nagashima", "永島 昭浩"),
        ("Hiromitsu Isogai", "磯貝 洋光"),
        ("Masanobu Matsunami", "松波 正信"),
        ("Takahiro Shimada", "島田 貴裕"),
        ("Kazuaki Koezuka", "肥塚 一晃"),
        ("Susumu Uemura", "植村 晋"),
        ("Yoshiyuki Matsuyama", "松山 吉之"),
    ),
    9: (
        ("Kazuya Maekawa", "前川 和也"),
        ("Hiroshi Matsuda", "松田 浩"),
        ("Von der Burg", "フォンデルブルグ"),
        ("Kenichi Uemura", "上村 健一"),
        ("Tomohiro Katanosaka", "片野坂 知宏"),
        ("Mitsuaki Kojima", "小島 光顕"),
        ("Hajime Moriyasu", "森保 一"),
        ("Yahiro Kazama", "風間 八宏"),
        ("Noh Jung-yoon", "盧 廷潤"),
        ("Takuya Takagi", "高木 琢也"),
        ("Cerny", "チェルニー"),
        ("Yoshiro Moriyama", "森山 佳郎"),
        ("Takumi Shima", "島 卓視"),
        ("Yasutaka Yoshida", "吉田 安孝"),
        ("Hiroshige Yanagimoto", "柳本 啓成"),
    ),
}

PLAYERS: Final[dict[tuple[int, int], tuple[str, str]]] = {
    (team, number): names
    for team, squad in _SQUADS.items()
    for number, names in enumerate(squad, start=1)
}


def ident_of(team: int, number: int) -> int:
    """A card's number: its team's block of 16, then the player's slot, 0 for the team."""
    return team * TEAM_SLOTS + number


def names_of(ident: int) -> tuple[str, str]:
    """A card's name in both languages: the player's, or the team's for a team card."""
    team, number = divmod(ident, TEAM_SLOTS)
    return TEAMS[team] if number == 0 else PLAYERS[team, number]


def card_named(typed: str) -> int:
    """The card a typed name or number means, or a ValueError naming what was not found."""
    wanted = typed.strip()
    known = {ident_of(team, 0): names for team, names in TEAMS.items()} | {
        ident_of(*key): names for key, names in PLAYERS.items()
    }
    if wanted.isdigit() and int(wanted) in known:
        return int(wanted)
    folded = wanted.casefold()
    for ident, (english, japanese) in known.items():
        if folded in {english.casefold(), japanese, japanese.replace(" ", "")}:
            return ident
    message = Said(
        f"unknown J.League card {typed!r}; name a team or a player",
        f"Jリーグ スーパートッププレイヤーズに {typed!r} という カードは ない。"
        "チームか せんしゅの なまえに して",
    )
    raise ValueError(message)
