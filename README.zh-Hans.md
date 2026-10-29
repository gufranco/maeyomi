<div align="center">

# maeyomi

<strong>为条码战士系列主机和用条码游玩的游戏打印可用的卡片。</strong>

[English](README.md) | [日本語](README.ja.md) | 简体中文 | [繁體中文 (香港)](README.zh-HK.md)

[![ci](https://img.shields.io/github/actions/workflow/status/gufranco/maeyomi/ci.yml?branch=main&style=flat-square&label=ci)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/gufranco/maeyomi?style=flat-square&label=release)](https://github.com/gufranco/maeyomi/releases/latest)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=flat-square)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![license](https://img.shields.io/github/license/gufranco/maeyomi?style=flat-square&label=license)](LICENSE)

<p align="center">
  <a href="#支持的主机和游戏">支持的主机和游戏</a> |
  <a href="#安装">安装</a> |
  <a href="#打开它">打开它</a> |
  <a href="#在命令行中">命令行</a> |
  <a href="#主机和游戏">主机和游戏</a> |
  <a href="#实体卡片">实体卡片</a> |
  <a href="#出处">出处</a>
</p>

</div>

已采录官方卡片 **3046** 张。日本食品 **2958** 件。特殊能力 **100** 种。每张卡片都用英语和日语两种语言印刷。测试覆盖率 **100%**。条码战士 II 的卡片已在实机上验证。

---

条码战士系列主机，以及一批 Famicom、Super Famicom 和 Game Boy 游戏，仅凭条码的数字就推导出一名战士、一件道具或一种效果。本程序把这套运算反向求解：要一张防御 2400 的护甲卡，它就算出主机会那样读取的条码，再打印出来。maeyomi 是条码战士对正面读取的称呼，也就是读出一名战士的那种读法。

它涵盖四台独立主机，即三台条码战士和世嘉玩具的「电视与茶札 茶犬『呼』与生活」，以及 32 款游戏：六款读取部在卡带里的 Famicom 用 Datach 游戏；十三款从插在主机上的条码战士 II 取得代码的 Famicom 和 Super Famicom 游戏；五款通过南梦宫的 Barcode Boy 读取的 Game Boy 游戏；带有自己读取器的 Game Boy 游戏「条码对战 Bardigun」；三款通过世嘉 HCV-1000 读取 Code 39 卡片的任天堂 DS 游戏，即「玩卡片吧! 第一次的 DS」、「时尚魔女 Love and Berry DS 收藏集」和「甲虫王者 Mushiking 超级收藏集」；以及通过插在麦克风口的扫描器读取 Code 128 卡片的两款任天堂 DS 游戏「Wantame 音乐频道 随处风格」和「流星洛克人 Dragon」；还有卡片带一条条纹轨道的世嘉玩具 Advanced Pico Beena 游戏「电车大集合! 玩卡片吧」和「前进吧! 面包超人 用卡片快乐学 ABC」。对其中每一个，它都能打印出条码已知的发售卡片、一张按要求定制的卡片，以及一张作弊卡：该设备会读取的最强或最有用的卡片。

每款游戏的规则都是从游戏自身的程序里读出，并对照在 MAME 中运行的游戏核对。生成的每个条码在送上纸张之前都会再经过一次解码器，打印出的每一页都会光栅化后用条码阅读器读回。打印出的卡片已在实机条码战士 II 上刷过确认。

## 支持的主机和游戏

下面的每台主机和每款游戏，都是命令行上的一个 `--device`，也是网页上 **主机或游戏** 下的一个条目。主机、游戏及其卡包的照片见 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/scans/Japan/)。

| 主机或游戏 | 日文名称 | 运行于 | `--device` |
|---|---|---|---|
| Barcode Battler | バーコードバトラー | 独立主机 | `bb1` |
| Barcode Battler 2 | バーコードバトラー2 | 独立主机 | `bb2` |
| Barcode Battler 2 Double | バーコードバトラー2 ダブル | 独立主机 | `double` |
| TV Ocha-Ken | テレビとお茶札 お茶犬「ほっ」と生活 | 独立主机，通过其读卡器读取 | `ochaken` |
| Alice no Paint Adventure | アリスのペイントアドベンチャー | Super Famicom，通过条码战士 II 读取 | `alice` |
| Barcode Battler Senki | バーコードバトラー戦記 | Super Famicom，通过条码战士 II 读取 | `senki` |
| Donald Duck no Mahou no Boushi | ドナルドダックの魔法のぼうし | Super Famicom，通过条码战士 II 读取 | `donald` |
| Doraemon 2 | ドラえもん2 のび太のトイズランド大冒険 | Super Famicom，通过条码战士 II 读取 | `doraemon2` |
| Doraemon 3 | ドラえもん3 のび太と時の宝玉 | Super Famicom，通过条码战士 II 读取 | `doraemon3` |
| Doraemon: Yousei no Kuni | ドラえもん のび太と妖精の国 | Super Famicom，通过条码战士 II 读取 | `yousei` |
| Dragon Slayer II | ドラゴンスレイヤー英雄伝説II | Super Famicom，通过条码战士 II 读取 | `dslayer2` |
| Hatayama Hatch | はた山ハッチのパロ野球ニュース!実名版 | Super Famicom，通过条码战士 II 读取 | `hatayama` |
| J.League Excite Stage '94 | J.リーグエキサイトステージ'94 | Super Famicom，通过条码战士 II 读取 | `excite94` |
| J.League Excite Stage '95 | J.リーグエキサイトステージ'95 | Super Famicom，通过条码战士 II 读取 | `excite95` |
| Lupin III | ルパン三世 伝説の秘宝を追え! | Super Famicom，通过条码战士 II 读取 | `lupin` |
| Spider-Man: Lethal Foes | スパイダーマン リーサルフォーズ | Super Famicom，通过条码战士 II 读取 | `spiderman` |
| Datach Battle Rush | データック バトルラッシュ | Famicom Datach | `battlerush` |
| Datach Dragon Ball Z | データック ドラゴンボールZ | Famicom Datach | `dbz` |
| Datach J.League | データック Jリーグ スーパートッププレイヤーズ | Famicom Datach | `jleague` |
| Datach SD Gundam Wars | データック SDガンダム ガンダムウォーズ | Famicom Datach | `sdgundam` |
| Datach Ultraman Club | データック ウルトラマン倶楽部 | Famicom Datach | `ultraman` |
| Datach Yu Yu Hakusho | データック 幽遊白書 | Famicom Datach | `yuyu` |
| Barcode World | バーコードワールド | Famicom，通过条码战士 II 读取 | `barcodeworld` |
| Battle Space | バトルスペース | Game Boy，通过 Barcode Boy 读取 | `bspace` |
| Monster Maker: Barcode Saga | モンスターメーカー バーコードサーガ | Game Boy，通过 Barcode Boy 读取 | `monstmkb` |
| Kattobi Road | カットビロード | Game Boy，通过 Barcode Boy 读取 | `kattobi` |
| Famista 3 | ファミスタ3 | Game Boy，通过 Barcode Boy 读取 | `famista3` |
| Family Jockey 2 | ファミリージョッキー2 名馬の血統 | Game Boy，通过 Barcode Boy 读取 | `famjock2` |
| Barcode Taisen Bardigun | バーコード対戦バーディガン | Game Boy，通过自带读取器读取 | `bardigun` |
| Card de Asobu! Hajimete no DS | カードであそぶ! はじめてのDS | 任天堂 DS，通过世嘉 HCV-1000 读取 | `cardasobu` |
| Oshare Majo Love and Berry | オシャレ魔女 ラブandベリー DSコレクション | 任天堂 DS，通过世嘉 HCV-1000 读取 | `osharemajo` |
| Mushiking Super Collection | 甲虫王者ムシキング スーパーコレクション | 任天堂 DS，通过世嘉 HCV-1000 读取 | `mushiking` |
| Wantame Music Channel | ワンタメ ミュージックチャンネル どこでもスタイル | 任天堂 DS，通过麦克风口上的扫描器读取 | `wantame` |
| Ryuusei no Rockman Dragon | 流星のロックマン ドラゴン | 任天堂 DS，通过麦克风口上的 Wave Scanner 读取 | `rockman` |
| Densha Daishuugou | 電車大集合! カードであそぼう | Advanced Pico Beena，通过其读卡器读取 | `densha` |
| Anpanman Card de Tanoshiku ABC | それいけ! アンパンマン カードでたのしく ABC | Advanced Pico Beena，通过其读卡器读取 | `anpanman` |

## 安装

```bash
brew install gufranco/tap/maeyomi
```

配方放在 [gufranco/homebrew-tap](https://github.com/gufranco/homebrew-tap)，一个在我的各个工具间共用、只放配方的小 tap，所以 tap 它只是一次快速克隆，而且每次发布都会自动在那里开一个 pull request。

安装会拉入 Python 3.14，并依据提交进仓库的锁文件构建一个隔离环境，于是你得到的是测试所用的版本，什么都不会落进你自己的 Python。

若改从检出的源码运行，执行 `uv sync --extra ui`，并在下面每条命令前加上 `uv run`。

## 打开它

```bash
maeyomi web
```

这会启动一个本地页面并用浏览器打开它。本程序所做的一切都在里面，所以从这一点往下都不是必读的。页面用一句话说明它的用途：

> Playable cards for Barcode Battler machines and barcode games, printed in English and Japanese.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/one-card-dark.png">
  <img alt="The card maker, with a fighter designed on the left and the printable card drawn on the right" src="assets/screenshots/one-card-light.png">
</picture>

用滑块设计一名战士，看着卡片随你移动滑块而重绘，然后打印。下方的面板会说明主机是否会读回你所要的那些数字，并显示它算出的条码。

**主机或游戏** 在页面最上方，从 [支持的主机和游戏](#支持的主机和游戏) 的表里那 32 项中选出卡片是为谁而做的。每个标签页都随它变化：制卡器只显示该设备会读取的字段，并把滑块停在该设备的上限；随机整版和超市按该设备的方式读取每个条码；**实体卡片** 只列出该设备的卡组，并在有卡组选择时将其隐藏；**作弊** 显示该设备的作弊卡，默认把每一种一起显示。同一个条码在每台设备上都是不同的卡片。选择另一台会清空每个标签页并回到制卡器，其卡片随数字变化而重绘。选择会记在地址里，如 `?device=dbz`，于是一个链接或一次重新加载都会打开同一个，而后退按钮会回到上一个；`/` 跳到列表上方的筛选框，回车选中它的第一个匹配项。在命令行上，`--device` 对 `generate`、`decode`、`cheat`、`random`、`products`、`kinds`、`abilities` 和 `official` 都起同样的作用。

五款任天堂 DS 游戏、两款 Beena 游戏和 TV Ocha-Ken 只读取它们自己的卡片，所用读取器接受 Code 39、Code 128 或条纹，而不是购物上的条码，所以页面会为它们作出调整。它们的随机整版取自游戏自己的列表，Battle Rush 的也一样，并且不保留任何数字区间，卡片不带数字的游戏也会把这些隐藏起来。**超市** 会说明货架上没有一样是给它们的卡片，**作弊** 会说明为什么卡片不带数字的游戏没有作弊卡，两者都指向 **实体卡片** 和 **单张卡片**。**读取条码** 询问卡片条码下方印着的号码。条纹卡片在那里不印数字，所以它靠卡片上印的卡号来读取，或靠每个位置按一个按钮来对齐它的条纹；`--character` 也接受那个号码。

**你已经拥有的任何条码也是一张卡片。** 把购物上的数字输入 **读取条码**，页面就会显示设备把它当成什么。这个是一瓶可口可乐，机器把它读作一件价值 2400 防御的护甲。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/read-a-barcode-dark.png">
  <img alt="A bottle of Coca-Cola typed in as a barcode, read back as an armour card worth 2400 defence" src="assets/screenshots/read-a-barcode-light.png">
</picture>

**超市** 存有 2958 件真实的日本食品，这样不去采购也能玩一局。搜索它，或者按 **给我惊喜** 并打印得到的那九件。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/supermarket-dark.png">
  <img alt="The supermarket tab, listing real Japanese groceries with the stats the device reads from each barcode" src="assets/screenshots/supermarket-light.png">
</picture>

其余三个标签页分别打印一版随机卡片、为这些主机和游戏发售的 3046 张卡片，以及所选主机或游戏会读取的最强卡片。页面有英语和日语两种，用顶部的按钮切换。

`maeyomi web --no-open` 启动服务器而不开浏览器，`maeyomi serve` 则是给没有浏览器的机器用的同一件事。

## 在命令行中

上面每个标签页也都是一条命令，每条都接受 `--device`，取 [支持的主机和游戏](#支持的主机和游戏) 表里的任何名称。不带它时，命令为条码战士 II 制卡，也就是下面示例所做的。

一版 24 张随机卡片，每 A4 页九张，可由种子复现：

```bash
maeyomi random --count 24 --hp 1000-10000 --st 100-3000 --df 100-3000 \
    --seed 1234 --output cards.pdf
```

一张按确切规格制作的卡片：

```bash
maeyomi generate --name "Fire Knight" \
    --hp 5000 --attack 1800 --defense 1200 \
    --race human --class warrior --ability 17 \
    --output fire-knight.pdf
```

它会把你所要的与得出的并排打印，于是一张有出入的卡片不会不被察觉：

```
Field    Requested       Generated       Difference
---------------------------------------------------
HP       5000            5000
ST       1800            1800
DF       1200            1200
PP       any             5
MP       any             0
Race     human           human
Job      -               0
Class    warrior         warrior
Speed    -               0
Ability  17              17
```

按设备读取条码的方式读取它：

```bash
maeyomi decode 0401207237501
```

设备用数字能力代码而非命名的元素。列出它们：

```bash
maeyomi abilities
```

道具也是同样做出来的。武器只带攻击，护甲只带防御，辅助道具只带一样东西：生命、草药或魔法点。草药和魔法点是 0 到 99 的纯计数：

```bash
maeyomi generate --name "Herb Pouch" --race support_item --herbs 99 \
    --output herbs.pdf
```

每个数值选项都接受一个确切值、一个区间或一个界限：`5000`、`5000-6000`、`>=1500`、`<=3000`。加 `--images png` 可在 PDF 之外导出页面图像。

当一个请求无法被精确满足时，`generate` 会说明哪个字段挡住了它，并且什么都不写。加 `--nearest` 以改取最接近、可达成的卡片：

```bash
maeyomi generate --hp 20900 --st 11000 --df 10000 \
    --race mechanical --nearest --output golem.pdf
```

```
closest card differs by 100 across the requested stats
  df: requested 10000, produced 9900
```

这个距离是在以显示单位计的 HP、ST 和 DF 上的差额之和，只计入请求所约束的那些数值。种族、职业、工作、能力和速度从不近似：对人类的请求不会因换成一只鸟而更好地被满足，所以受制于其中之一而被挡下的请求会原样返回，未被满足。

加 `--back-read` 可得一张设备从背面而非正面读取的卡片。那些卡片上限更低，49900 HP 对 99900，并且四个数字共同喂给数值和能力，所以可达成的组合要少得多。

## 主机和游戏

### Barcode Battler II

条码战士 II 是默认设备。它读取一个条码，仅凭数字推导出一名战士或一件道具，从正面读取，或者对一张反向刷过的卡片，从背面读取。

#### 设备实际存储的东西

取自 [barcodebattler.net](https://barcodebattler.net/)，由解码器重现而非写死在其中。

| 属性 | 正面读取 | 背面读取 |
|---|---|---|
| HP | 0 到 99900 | 0 到 49900 |
| ST | 0 到 19900 | 0 到 11900 |
| DF | 0 到 19900 | 0 到 9900 |
| 特殊能力 | 00 到 99 | 00 到 29 |

种族 0 到 4 是角色：机械、动物、水生、鸟类、人类。种族 5 到 9 是道具。工作数字 0 到 6 是战士，7 到 9 是魔法师。数值以 100 为单位存储，所以每个数值都是 100 的倍数。

两条约束限制了可以要求的范围。命中其中之一的请求会被连同理由一起拒绝，从不被悄悄更改：

- 一个 HP 高于 19900 的角色需要公布的正面读取标记，它会把第三个数字强制为 9。这样一张卡片的 HP 总是以 900 结尾，速度总是 5。
- 种族 0、1 和 2 在 HP 高于 20000 时其攻击和防御会被改写，所以在那个大小上并非每一对数值都可达成。其中一些代码让设备以比它显示的更高的攻击或防御作战，最高到 24600；卡片也会把那个值印出来。

#### 它如何运作

```
requested attributes -> digit placement -> barcode -> decoder -> compare -> accept
```

正面读取把固定的数字切片映射到属性上，所以把它反过来是放置而非搜索：一个完全指定的请求决定每一个数字，校验位再计算出来，于是只剩一个候选，而非暴力枚举要走的 10^12 个。每个候选仍会再经过解码器，在任一字段上不一致的那个会被丢弃。

背面读取不是双射。四个数字共同喂给生命、攻击、防御和能力，而种族落在校验位的位置上，所以它无法被放置，只能通过调整一个自由数字来得到。可达成的集合小到可以直接枚举：10000 个数字组合产生 5000 个不同的数值三元组，因为生命的百位数字被减半。

条码以矢量绘制，采用显式的模块宽度，默认为 EAN 标称的 0.33 mm。一个为适配版面而缩放的光栅化条码会把它的模块参差不齐地取整而停止扫描，这是任何对数字串的测试都抓不到的。

### 第一代 Barcode Battler

第一代条码战士，1991 年的，用它自己的方式读取同样的数字：每名战士都是战士，生命止于 19900，攻击和防御止于 9900，而那个两位代码是来自另一张表的一个标志，所以 18 是英雄，而在 II 上它使攻击翻倍。为 `decode`、`generate` 和 `cheat` 加 `--device bb1` 可为它制卡。它的解码器从为它写的四个列表中重现了 113 张公布的卡片，而尚无一张它的卡片在实体第一代条码战士上读过，这一点它的每一版都会写明。

### Barcode Battler II Double

条码战士 II Double，即 1993 年的 II²，没有读取器，从一台 II 取得代码。它按 II 的方式读取，只有一种例外：一个以 7 开头且第十位数字为 8 的代码，它会按自己的方式读取：攻击和防御达到 99900，而特殊能力是生命的两个数字。`--device double` 可为它制卡，以 [barcodebattler.net](https://barcodebattler.net/bb2c0.html) 上的「BBIIダブルC0」为出处。那种读法解释了正伝3 列表中十一张没有任何 II 读法能解释的卡片。它的种族是攻击的百位数字减 5，正如一份 [收藏者报告](https://mevius.5ch.net/test/read.cgi/toy/1226667612/) 在正伝3 和正伝4 的敌人卡上所发现的；十一张全都吻合，而百位数字低于 5 时种族未知。它的速度仍然未知。Double 还命名了 II 没有的两个职业，工作 4 的祭司和工作 6 的圣战士，并有它自己的特殊能力表。

### Datach 游戏

Datach 是万代为 Famicom 做的条码读取器，一个带有插槽、用来插游戏自己较小卡带的卡带。

万代的 Datach 龙珠 Z：激斗天下第一武道会，一款 1992 年的 Famicom 游戏，附带一个条码读取器。`--device dbz` 可为它制卡。游戏把十个数字的比特打散进一个 40 位的数，并从中读出一名战士或一件道具、一个必杀技等级、HP、BP 和 DP。那条规则是从游戏自己的程序里读出的，而解码器在 MAME 中运行的游戏接受的 232 个代码上每一个都与游戏一致。用 `--character` 按游戏显示的名字或其 id 选出战士或道具，用 `--level` 选等级，用 `--hp`、`--bp` 和 `--dp` 选数字，加 `--nearest` 则在那些确切数字无法打印时改取最接近的可打印卡片；一名数字足够高的战士会变成它更强的形态，正如游戏那样。尚无一张它的卡片由实体 Datach 读过，这一点它的每一版都会写明。

万代的第二款 Datach 游戏、1993 年的 Datach 奥特曼俱乐部：Supokon Fight!，把一个条码读入 51 种类型之一，0 到 27 的奥特英雄和怪兽以及 32 往上的道具，还有它称为 PW、ST 和 SP 的三个数字，每个 0 到 9900、以 100 为步长。`--device ultraman` 可为它制卡：用 `--character` 按游戏显示的名字或其编号选类型，用 `--hp`、`--st` 和 `--df` 按那个顺序选三个数字。那个区间内的每个值都可打印。规则是从游戏程序里读出的，并在 MAME 中运行的游戏本身上，于其 38 张发售卡片和每种类型各建一个共 51 个代码上一致。尚无一张它的卡片由实体 Datach 读过。

同为 1993 年的 Datach SD 高达：高达大战，把一个条码读作 63 架机动战士之一或 59 张指令卡之一。一架机动战士从它自己的 HP、AP、DP 和 CP 起步，给每一项加上一张表中的加成，并带一件近程和一件远程武器中的其中之一；一张指令卡带它的效果和它花费的 CP。`--device sdgundam` 可为它制卡：用 `--character` 按名字、型号或编号选卡，用 `--hp`、`--st` 和 `--df` 选数字，即 HP、AP 和 DP，用 `--pick sr=1`、`--pick lr=5` 或 `--pick cp=11` 选武器和 CP。一个夹在游戏能持有的两个值之间的数字会变成最接近的那个，命令会说明。规则在 MAME 中于其 76 个发售条码和每个槽各建一个共 122 个代码上与游戏一致。尚无一张它的卡片由实体 Datach 读过。

同为 1993 年的 Datach 幽游白书：暴斗暗黑武术会，把一个条码读作 22 名斗士或 10 件道具之一，外加游戏藏起的一名斗士。一名斗士的 HP 和 SP 是它自己的，没有条码能改变它们；条码选的是它能用其四种招式中的哪些。一件道具按四个等级之一加 HP 或 SP，或改变对战模式的一条规则。`--device yuyu` 可为它制卡：用 `--character` 选卡，用 `--pick moves=15` 选它的招式，每个招式一个比特，用 `--pick level=3` 选一件道具的等级。规则在 MAME 中于其 37 张发售卡片和跨每个角色、面具与道具所建的 183 个代码上与游戏一致。尚无一张它的卡片由实体 Datach 读过。

1994 年的 Datach J 联赛超级顶级球员，把一个条码读作 1993 年 J 联赛十家俱乐部的 150 名球员之一，或读作那些俱乐部之一。一张卡片命名一位真实球员，自身不带任何数字。游戏的程序为每位球员保留一份档案、一张脸和一个外观，没有任何能力，所以没有一张卡片比另一张更强，也没有它的作弊卡。`--device jleague` 可为它制卡：用 `--character` 按名字或编号选球员或俱乐部。规则在 MAME 中于其 160 个发售条码和为触及游戏允许的每个折叠值所建的 12 个代码上与游戏一致。尚无一张它的卡片由实体 Datach 读过。

蜡笔小新：我和 Poi Poi，一款 Datach 游戏，其程序里根本没有任何条码读取，所以它无法接受一张卡片。

Datach Battle Rush：Build Up Robot Tournament 在它的 Robo Factory 用按顺序刷入的两张卡片造出一个机器人，而 `--device battlerush` 制作这一对。第一张卡片带机器人的编号、头、身、肩、脚和驾驶员；第二张带它的武器和四个等级。游戏故意拒绝商店的条码：它自己卡片的最后一位数字比一个 EAN 本会有的校验位低一或两，所以这些卡片以那个数字打印，没有普通的条码阅读器会接受它们。用 `--character` 按编号或按 16 名对手之一的名字选机器人，用 `--pick head=3 --pick attack=7` 等选它的部件和等级。规则是从游戏程序里读出的，并在 MAME 中于试过的每一对上与之一致；MAME 只部分模拟游戏的存档芯片，所以这些核对会写入它的两个字节以抵达工厂。无人知道万代印了哪些卡片的列表。

### 通过条码战士 II 读取的游戏

这些 Famicom 和 Super Famicom 游戏没有自己的读取器。一台插在主机上的条码战士 II 读取卡片并把数字送过去。

Sunsoft 的 Barcode World，一款 1992 年的 Famicom 游戏，通过连到 Famicom 的一台条码战士 II 取得卡片，所以它读取每一个条码。`--device barcodeworld` 可为它制卡。游戏读取数字的方式与条码战士 II 很像，以百为单位：HP 最高 49900，ST 和 DF 最高 19900，其中任何高于 19900 的生命都需要百位上有个 9 且速度为 5，而魔法和草药来自工作。用 `--character` 选一名战士或魔法师，用 `--hp`、`--st` 和 `--df` 选数字，用 `--pick job=3`、`--pick speed=8` 和 `--pick ability=45` 选工作、速度和能力。规则在 MAME 中于 211 个代码上与游戏一致，其中有它的 24 张发售卡片，也于此处所建、试过的每一张卡片上一致。

Epoch 的 Barcode Battler 战记，一款 1993 年的 Super Famicom 游戏，通过 Barcode Battler II 接口上的一台条码战士 II 取得卡片，而 `--device senki` 可为它制卡。它按 Barcode World 的方式读取数字，有三处不同。一个 8 位代码会带着前面五个零到来，因为接口把条码战士 II 的空格变成了零。一件从末端读取的道具其攻击的个位保持在十以下。而印在接口自己盒子上的代码会在任一战斗模式中打开音效测试，而不是制作一张卡片。规则在 MAME 中于 253 个代码上与游戏一致，其中有此处所建、试过的每一张卡片。剧情模式的一个隐藏商店「黑店」，会以更小的偏移读取一张从末端读取的卡片，所以这样一张卡片也会显示商店给它的 HP、ST 和 DF；那种读法在 MAME 中于 232 个代码上与游戏一致，这些代码是通过设置商店地图事件所设的那个标志而非走到那里来达到的。MAME 0.289 把每个数字送给 Super Famicom 时错开一位，所以这些核对通过一个为它们而写的接口把游戏喂进去。

另外四款 Epoch 的 Super Famicom 游戏通过同一个接口在它们的密码画面读取一个代码，每个代码触发一张固定列表里的一个效果，而不是制作一名战士：Lupin III：追寻传说的秘宝! 用 `--device lupin`，Donald Duck no Mahou no Boushi 用 `--device donald`，Spider-Man：Lethal Foes 用 `--device spiderman`，Alice no Paint Adventure 用 `--device alice`。这些效果是诸如无伤、无限命或满道具这样的作弊，跳到某一关、某一章或某个结局，以及音效测试。`maeyomi kinds --device lupin` 列出一款游戏的效果，`--character` 按名字或编号选出一个。每条规则都是从游戏程序里读出的，并在 MAME 中于试过的每个代码上与游戏一致：Lupin III 为 250 个，Donald Duck 为 247 个，Spider-Man 为 221 个，Alice 为 253 个。一个不匹配任何规则的代码会被读取而什么也不做。

三款 Super Famicom 的哆啦A梦游戏各在两个画面上按同样的方式读取代码：哆啦A梦 2 用 `--device doraemon2`，在其密码画面和某一关的道具菜单里；哆啦A梦 3 用 `--device doraemon3`，在其密码画面和游玩中的装备菜单里；大雄与妖精之国用 `--device yousei`，在其密码画面和城镇地图的道具画面上。密码画面给出诸如无敌、99 条命或更靠后世界这样的作弊，菜单给出秘密道具、武器、护具和物品。每张卡片都写明要在哪个画面刷它。哆啦A梦 4 带有同样的读取代码，却从不调用它，所以它里面没有画面接受条码。

J 联赛 Excite Stage '94 在赛季前比赛之前，于其阵容画面的条码战士面板上读取一个代码，而 `--device excite94` 可为它制卡。一个校验位为 4 或更大的代码是 240 名隐藏球员之一，每人有一个名字和踢、射、跑、盘带的等级，或者对一名门将是防守；一个更低的校验位是一张像 Excite Stage '95 那样的道具卡。用 `--character` 选一名球员或一件道具，用 `--pick value=253` 选一件道具的数量。名字和等级直接来自游戏自己的表，除一名其数字无法由任何代码的数字触及的球员外，每名球员都能打印。PK 模式按同样的方式读取一名球员，并按它自己的方式把一张道具卡读作六种 PK 道具之一，踢球速度、控制、弧线球、扑救、敏捷或即时扑救，等级从 0 到 9，卡片也会显示。两条规则在 MAME 中于试过的每个代码上与游戏一致，PK 模式中为 168 个。

Super Famicom 的 J 联赛 Excite Stage '95，在一场公开赛、一个联赛、一个锦标赛或一场梦幻赛之前，于其条码战士 II 输入画面读取一个代码，而 `--device excite95` 可为它制卡。每个代码是一张道具卡：整体能力、盘带、传球速度、踢球速度或门将的扑救，提升 0 到 253，或者一张特殊卡，给最多 4 点让分，或给不显示卡片的犯规。用 `--character` 选道具，用 `--pick value=253` 选数量。PK 模式把同一个代码读作四种 PK 道具之一，球速、射门准度、门将速度或门将等级，提升一级，卡片会显示是哪一个。两种读法在 MAME 中于试过的每个代码上与游戏一致，PK 模式中为 70 个。

Falcom 的 Dragon Slayer：英雄传说 II，由 Epoch 于 1993 年为 Super Famicom 发行，在其标题菜单和战场菜单里读取一个代码，而 `--device dslayer2` 可为它制卡。标题菜单给出诸如全状态最高、经验与金钱翻倍、怪物列表或音效模式这样的作弊。在战场里，以 038438816 开头的代码给出其末三位数所指的道具，999 开启所有传送点，少数代码无需拥有即可使用提灯、Bisna 果、休息蘑菇或地图。在 Epoch 为条码战士 II 印的 Dragon Slayer 卡片中，游戏认得 Selios：在标题菜单上刷它，会把英雄的每项状态设为最高。

はた山ハッチのパロ野球ニュース! 实名版，Epoch 1993 年的棒球游戏，在其 Battle Baseball Board 上把一个代码读作一名战士，而 `--device hatayama` 可为它制卡。一个按 Epoch 卡片的布局排列的代码会被就地读取：体力最高 99900，攻击和防御最高 19900、以百为单位，而一名法师的魔法最高 99；任何其他代码都从它的末几位数算出。用 `--character` 选一名战士或法师，用 `--hp`、`--st` 和 `--df` 选数字，用 `--pick mp=99` 选魔法。同一个代码的最后一位数字还会在游戏另外两个条码画面上选一个战术和一个图形，每张卡片都会印出是哪个。游戏附带 14 支球队的卡片，而无人公布过它们的条码。

### 通过 Barcode Boy 读取的 Game Boy 游戏

Barcode Boy 是南梦宫为 Game Boy 做的读取器，它通过连接端口把数字送过去。

Battle Space，南梦宫 1992 年随其 Barcode Boy 读取器一起为 Game Boy 发售的游戏，把一个代码读作一名战士，而 `--device bspace` 可为它制卡。游戏从条码造出十三个新数字，并把它们读作 HP、MP、AP 和 DP，其状态画面以乘以一百显示。这四项相对游戏阈值所处的位置决定 98 个职业之一，而职业固定了魔法，三组法术之一或没有，以及必杀技。用 `--character` 选一个职业，用 `--hp`、`--st` 和 `--df` 选 HP、AP 和 DP；程序会选出能保住该职业的最高 MP，并把它印在卡片上。MAME 没有 Barcode Boy，所以一个脚本按读取器的方式回应 Game Boy 的连接端口，而解码器在给它的全部 668 个代码上与游戏一致，其中有为每个职业各建一张的卡片。

Monster Maker：Barcode Saga，南梦宫 1993 年的 Barcode Boy 游戏，把一张卡片读取两种方式，而 `--device monstmkb` 可为它制卡。组队时，一张卡片给出 17 名 1 级英雄之一。游戏后期，同一张卡片给出 35 名角色之一：一名 1 到 9 级的英雄，或 18 名其他角色之一，其中有怪兽。一个以 9 开头的代码用第三到第五位数命名它的英雄，任何其他代码用第六和第八位数，而第一、三、五位数设定后期的等级。用 `--character` 选英雄，用 `--pick later=` 选卡片后期给出的东西，即角色编号乘以一百再加它的等级：`--pick later=1709` 让 Lorian 以 9 级回归，`--pick later=2000` 在 Link 上给出 Dragon。在 MAME 中，每个代码都在组队画面读取两次，一次按新游戏读取它，一次带游戏后期所设的标志，而解码器在全部 830 个代码的两种读法上都与游戏一致，其中有程序能造出的每一张卡片。

Kattobi Road，南梦宫 1993 年的赛车游戏，把一张卡片读作它所保留的 256 辆车之一，而 `--device kattobi` 可为它制卡。只有代码的末五位数算数。头两位和末两位选车，再和中间那位一起把它的马力设在该车自身的 30 PS 以内、扭矩在 5 kg-m 以内。卡片显示车的类别、马力、重量和扭矩。用 `--character` 按编号或按名字选一辆车，程序会打印给它最高马力的那个代码。车名按游戏显示的样子命名，它们的英文名按规则罗马化。解码器在给它的全部 592 个代码上与 MAME 中的游戏一致，其中有为每辆车各建一张。

Famista 3，南梦宫 1993 年的棒球游戏，在球队编辑中把一张卡片读作一名新秀打者或投手，而 `--device famista3` 可为它制卡。游戏不从数字造出球员：其中两位决定打者或投手，最后一位选出它的一组球员数据，其余的成对指向其中一名球员，其数字被原样复制。打者显示其左右、打击率、本垒打和速度，投手显示其左右、防御率、球速和耐力。用 `--character` 选打者或投手，用 `--pick player=` 选一个代码能触及的 833 名打者或 384 名投手之一；页面按从强到弱列出他们。解码器在给它的全部 1551 个代码上与 MAME 中的游戏一致，其中有为每名球员各建一张，以及游戏用它们自己规则读取的八位代码。

Family Jockey 2，南梦宫 1993 年的赛马游戏，把一张卡片读作一匹赛马、一匹母马或一匹种马，取决于它从哪个菜单被刷，而 `--device famjock2` 可为它制卡。每个菜单把第七到第十二位数变成速度、耐力、斗志、跳跃、加速和类型，从 0 到 9，再加上由所有数字之和选出的、来自它自己表的键，所以一张卡片是三匹不同的马。卡片在其图块上显示赛马，在其面板里显示另外两匹。用 `--character` 选菜单，用 `--pick speed=`、`stamina=`、`guts=`、`jump=`、`turbo=` 和 `type=` 选每个数字；任何省略的都是 9。游戏还认得南梦宫自己游戏盒的七个条码，带着一个的卡片会赢得游戏所命名的奖励：某一个数字再多两点，或者对 Barcode Boy 自己的卡片，全部六个各再多一点。没有数字超过 10。解码器在三个菜单各给它的全部 459 个代码上与 MAME 中的游戏一致。

### Barcode Taisen Bardigun

条码对战 Bardigun，Tamsoft 1998 年的 Game Boy 游戏，随它自己接在连接端口上的条码读取器一起发售，并从在农场刷入的每一个条码孵化出一只生物 Barloid。`--device bardigun` 可为它制卡。在一个十三位代码里，第十一位数、1 到 7，选出七张各含十只 Barloid 的表之一，而校验位从中选出一只；一个八位代码从它的第三位和第一位数按同样方式读取。当表的数字是 0、8 或 9 时，蛋随机孵化。一只 Barloid 带着它自己的力量、智慧、强韧、速度和 HP 孵出，卡片会显示。用 `--character` 选一个代码确保能孵出的 35 只 Barloid 之一。解码器在给它的全部 104 个代码上与 MAME 中的游戏一致，其中有每张表和每个校验位。

### Card de Asobu! Hajimete no DS

玩卡片吧! 第一次的 DS，世嘉 2007 年的任天堂 DS 游戏，通过世嘉的 HCV-1000 读取卡片，那是一个插进第二插槽、接受 Code 39 的读取器，而 `--device cardasobu` 可为它制卡。每张卡片教一个假名，还有一张开始找卡片。当一张卡片文本的前十个字符匹配游戏自己表里的一个、且其余是 V01 时，游戏才接受它，所以这些卡片不带数字，也没有作弊卡。用 `--character` 按假名顺序、英文名或日文名选 46 张卡片之一。一张卡片以每模块 0.22 mm 印出它的 Code 39 符号，那是卡片放得下的最宽值。没有其他模拟器有 HCV-1000，所以游戏在 GBE+ 中运行，构建于一个固定提交并带一个重放脚本化刷卡的小补丁：它接受全部 46 张卡片中的每一张，并拒绝一个错误版本、一个没有卡片带有的代码，以及它的表为 か 保留的那个空槽。

### Oshare Majo Love and Berry DS Collection

时尚魔女 Love and Berry DS 收藏集，世嘉 2006 年的任天堂 DS 游戏，通过同一个 HCV-1000 读取 Love and Berry 街机卡片并解锁每张所带的物品，而 `--device osharemajo` 可为它制卡。一张卡片的十一个字符是一道密码：第二个选出四个字母表的顺序，接下来八个拼出两个 33 进制数，而那些数的反转半字节是一个类别、一个代码、一个编号和若干校验，其中有一个取模 15 的和。一张通过的卡片命名一件物品，如 CB004，一条裙子。游戏为一张卡片能给出的每件物品保留一张卡片图像，跨裙子、发型与妆容、鞋子和特殊卡共 281 张，这些就是它打印的卡片；用 `--character` 按其代码选一张。它们不带数字，所以没有作弊卡。密码是从游戏程序里读出，并通过在 Unicorn 引擎中运行游戏自己的解码器、即 $020022EC 处的例程来核对的：该移植在给它的全部 1396 个代码上与之一致，其中有为每件物品各建的一张、GBE+ 的笔记列出的六张卡片，以及游戏以 N 开头、A 结尾的较短形式的代码。

### Mushiking Super Collection

甲虫王者 Mushiking 超级收藏集，世嘉 2007 年的任天堂 DS 游戏，通过 HCV-1000 读取 Mushiking 街机卡片，而 `--device mushiking` 可为它制卡。游戏把它的卡片保存为若干十三字符代码的列表，五个在它自己的一个文件里，两个在它的程序里，并取它们之中代码匹配的第一张卡片。一个以 FFF 结尾的代码靠它的前十个字符匹配，而末三个选出一个版本：MKF、RH5、NCI、BTF 和 KWG 各命名一个，其他任何的则是卡片自己的。这些卡片以它们自己的代码打印，共 535 张：以卡上甲虫或角色命名的甲虫卡和伙伴卡，以及按编号排的招式、执照和额外卡。用 `--character` 按名字、代码或编号选一张。它们不带数字，所以没有作弊卡。列表是从游戏里读出，而匹配是通过在 Unicorn 引擎中运行游戏自己的比较例程来核对的：它在给它的全部 1347 个代码上一致，其中有每一张卡片、以 FFF 结尾的卡片的各版本，以及没有卡片带有的代码。

### Wantame Music Channel

Wantame 音乐频道 随处风格，Capcom 2007 年的任天堂 DS 游戏，通过一个坐在第二插槽、经麦克风口与 DS 对话的扫描器读取 Wantame 街机卡片，而 `--device wantame` 可为它制卡。扫描器读取一个十二位的 Code 128 条码，并把它的六对数字连同其后的 Code 128 校验和作为声音送出。游戏核对校验和，按第二对选出它的一张卡表，并且只有当全部六对都匹配其中一条记录时才接受一张卡片，所以没有按要求定制的卡片，也没有作弊卡。这些卡片以它们自己的代码打印，共 235 张：狗、服装、配饰和效果，各按游戏命名它的方式命名，并带着卡片上印的编号。还有一件服装 S36，会被找到然后在每个扫描的场景里用它自己的一条消息回应，什么也不给，所以它不被打印。用 `--character` 按名字、代码或编号选一张。这些表是从游戏程序里读出，而读取是通过在 Unicorn 引擎中运行游戏自己的校验和、卡片核对与卡片查找来核对的：它在给它的全部 390 个代码上一致，其中有每一张卡片和没有卡片带有的代码，并把每一个带错误校验和送来的都拒之门外。

### Ryuusei no Rockman Dragon

流星洛克人 Dragon，Capcom 2006 年的任天堂 DS 游戏，通过 Wave Scanner 读取 Wave Card，那是一个带自己屏幕、坐在第二插槽、经麦克风口与 DS 对话的玩具，而 `--device rockman` 可为它制卡。一张 Wave Card 带一个以 040000 开头的十二位 Code 128 条码，而 Wave Scanner 只把末三对送给游戏，每一对作为一个最高到 63 的数，在一个常量之后、一个校验字节之前。这些卡片以它们自己的代码打印，共 211 张：标准卡、mega 卡、giga 卡和角色卡，按 GBE+ 的笔记列出它们的方式命名和编号。三张角色卡带着一张战斗卡的代码，并挨着它命名。用 `--character` 按名字、代码、如 S-001 这样的卡号，或其在列表中的位置选一张。它们不带数字，所以没有作弊卡。列表和扫描器的布局来自 GBE+ 的笔记，而且与此处其他每个设备不同，游戏自己对它们的读取尚未核对：解码扫描器的那段例程还没在游戏程序里找到。

### Densha Daishuugou! Card de Asobou

电车大集合! 玩卡片吧，世嘉玩具 2006 年的 Advanced Pico Beena 游戏，通过 Beena 的读卡器读取电车卡片，而 `--device densha` 可为它制卡。一张 Beena 卡沿一条长边有十二个放条的位置：有条是一，空位是零，读取器把它们拼出的十二个比特交给游戏。这些位置是在 MAME 软件列表里真实卡片的扫描上测出的：条宽 2.88 mm，中心间距 6.28 mm，各长 15 mm 且在离边 0.4 mm 处结束，第一个离末端 10.07 mm。真实卡片是横向的，所以一张条纹卡横躺着打印，每 A4 页八张，轨道沿它的底边、第一个位置在左边，而正面从轨道上方 2 mm 开始，使没有颜色染黑一个空位。游戏只读取 50 张电车卡和一张测试卡，别无其他，所以没有按要求定制的卡片，也没有作弊卡。每张卡片以它所印的电车命名，如 200系 やまびこ，200 系 Yamabiko；第 16 张保留它的编号，因为 MAME 没有它的扫描。用 `--character` 按名字或如 04 这样的卡号选一张。每张卡片都在 MAME 中用 Beena 的 RD2061 读取器在车站页面上扫过，在那里一张卡片会调出它的电车或改变场景：试过的 138 个代码中，MAME 的 50 张卡片和它的测试卡会被读取，其余 87 个让页面原封不动。一张卡片的代码写成它的十二个位置，1 代表一条，如第 04 张卡的 100010110011。

### Soreike! Anpanman Card de Tanoshiku ABC

前进吧! 面包超人 用卡片快乐学 ABC，世嘉玩具 2006 年的 Beena 游戏，用同一个读取器、以同样的十二个放条位置读取卡片，而 `--device anpanman` 可为它制卡。MAME 软件列表里 50 张扫描中每一张上的条都拼出 MAME 给那张卡的值，间距与电车大集合的相差在 0.05 mm 以内，所以这些卡片以同样的轨道打印。游戏读取 26 张字母 A 到 Z 的卡片、24 张从 Apple 到 Chimpanzee 的英文单词图片卡，以及一张会调出其祝贺画面的测试卡，各按卡片所印命名。用 `--character` 按字母、单词或卡号选一张。每张卡片都在 MAME 中于游戏的第一页扫过，而游戏自己的内存说出了它取的是哪张卡：它保存卡片编号的那个字节在刷卡前被设为 255，而试过的 348 个代码中，游戏把它换成了 51 张卡片以及同样 51 张把第二个放条位置翻转后的正确编号，对其余 246 个则原样不动。无论那第二个位置是什么，游戏都会读取一张卡片，所以解码器也一样。

### TV Ocha-Ken

TV Ocha-Ken，世嘉玩具 2005 年的插进电视的机器，通过它的 RD1831 读卡器读取 Ocha-Ken 卡片，而 `--device ochaken` 可为它制卡。它启动 Beena 的 BIOS，但把它的游戏「电视与茶札 茶犬『呼』与生活」留在它自己的闪存里，而它的卡片带十六个放条位置而非十二个。在 MAME 的 TV Ocha-Ken 软件列表里全部 50 张扫描上，条都拼出 MAME 给那张卡的值。跨它们测出，条宽 3.93 mm，中心间距 4 mm，所以相邻的条几乎相碰；各长 8.17 mm，在离边 0.28 mm 处结束，第一个坐在离末端 14.23 mm 处，是约半毫米、从卡到卡这一跨度的中点。机器读取它的 50 张卡片，别无其他，所以没有按要求定制的卡片，也没有作弊卡。每张卡片以它所印的标题命名，如 和のお茶，日本茶，或 麦茶犬〈ムハ〉，Muha，大麦茶犬。用 `--character` 按名字或卡号选一张。每张卡片都在 MAME 中于新一天开始所进入的房间里、在 B 开始一局新游戏之后扫过：试过的 661 个代码中，50 张卡片各调出一个自己的场景，其余 611 个，即每张卡片翻转一个位置，让房间停在一张空白卡所停的地方。机器读取全部十六个位置，所以解码器也一样。一张卡片的代码写成它的十六个位置，1 代表一条，如第 01 张卡的 0101000000001001。

## 检查机器

`maeyomi doctor` 检查这台电脑能否打印出一张设备会读取的卡片，并打印每项检查看到的东西。它读取一个答案已知的条码，画一个符号并从 PDF 中把它解码回来，确认日语字体已解析，对照它的对比度和色盲阈值重新测量调色板，点数两个卡片列表，并报告什么在运行它、终端能否打印日语以及还剩多少空间。只有当确实出了问题时它才以非零退出。无论如何先运行它：一个没有解析的字体，否则会在打印出的卡片上表现为空白文字。

## 打印

以 100% 打印。关掉「适应页面」、「缩小以适合」和任何其他缩放。一个缩放过的页面看起来仍然正确，仍然会停止读取，因为扫描器测量的是模块宽度。

卡片竖着打印，扑克尺寸 63.5 乘 88.9 mm，每 A4 页九张；Beena 和 TV Ocha-Ken 的条纹卡横躺着，每页八张。那是卡套和切纸刀所适配的尺寸。这是本项目的选择：Epoch 从未公布它自己卡片的尺寸，也没有收藏页面、拍卖列表或 wiki 记录过它。尺寸存在 [`layout.py`](src/maeyomi/rendering/layout.py) 里的 `CARD_WIDTH_MM` 和 `CARD_HEIGHT_MM`，改这两个数会带动其余一切，因为网格、间隙、标记和适配检查全都由它们导出。

每一版都遵循印刷店所要求的：

| 度量 | 值 | 为什么 |
|---|---|---|
| 出血 | 整版上 1.5 mm，带 `--print-shop` 时 3 mm | 落点偏一点的裁切仍能找到油墨 |
| 卡片间的间隙 | 4 mm，出血的两倍 | 每张卡片在自己的线上裁切，而非与邻居共用一条 |
| 安全区 | 距裁切线 4 mm | 读者需要的东西都不坐在裁切会取走的地方 |
| 裁切标记 | 从出血边开始的角标 | 印刷者裁到的地方，没有线穿过卡片 |
| 模块宽度 | 0.330 mm | GS1 EAN-13 标称值 |
| 条高 | 22.85 mm | GS1 标称值，以及一次手刷容差的全部 |

`--print-shop` 写出同样的卡片所取的另一种形状：每页一张卡，页面尺寸为卡片加 3 mm 出血，没有标尺也没有标记，那是商业印刷者自己的说明所要求的。

每一版在它的页脚带一把以厘米标号的 100 mm 标尺，并在卡片上方有一行英语和日语，写明每个条码应测出的宽度。第一次打印后把一把尺子贴着它。若印出来短了，说明打印机缩放了页面；改正对话框再打印一次。两条带子都坐在卡片网格之外，所以它们会随裁下的边角一起离开。

## 读取你已经拥有的条码

`maeyomi decode 4901085061169` 打印设备会把任何条码读成什么，而 `-o card.pdf --name "Tomato sauce"` 还会把卡片打印出来。网页在 **读取条码** 下有同样的东西：输入印在条下的数字，它会显示卡片的种类、三个数字、特殊能力，以及设备从正面还是背面读取它，还有一张你可以打印的卡片。一张条纹卡的条下没有数字，所以它靠卡片上印的号码读取，如 `maeyomi decode --device ochaken 13`，而页面也提供每个位置一个按钮来对齐它的条纹。

`maeyomi kinds` 用两种语言列出设备认得的每一种卡片，以及每一种的作用。

这就是这台机器实际被玩的方式。任何商品条码都是一张卡片，所以一瓶番茄酱是一名战士，一包薯片是一件武器。日本商品代码和其他任何代码一样：`4902102072618`，一瓶茶，是一件价值 2400 防御的护甲。

## 超市

`maeyomi products --search 茶` 列出匹配的真实日本食品，`--count 9 --seed 3` 随机取一把，而 `-o shopping.pdf` 把它们打印出来。网页在 **超市** 下有同样的东西，带一个 **给我惊喜** 按钮。番茄酱对阵拉面是一场公平的较量。

这个货架是 [Open Food Facts](https://world.openfoodfacts.org/) 的一个精选子集，只留发给日本公司的条码，即 45 和 49 前缀，且有一个解码器接受的日语名称。它们的数据按 Open Database License 发布，这个子集沿用同样的条款，在 **出处** 下注明。卡片上没有一样东西来自它们：每个数字都由本项目的解码器从条码读出，所以一个错误的名字只会毁掉一个笑话，别无其他。

网页上的 `maeyomi decode <barcode>` 还会问 Open Food Facts 一个条码叫什么，在它知道时把名字填进去。这是一种便利：查找失败不改变卡片的任何东西。

## 实体卡片

`maeyomi official --list` 列出为这些设备发售的 54 个卡片列表、每个会打印多少张卡片，以及每个列表是为哪台设备而写的；`maeyomi official --set candy -o candy.pdf` 打印一个，而省略 `--set` 则打印全部 3046 张。网页在 **实体卡片** 下有同样的东西。

Epoch 从未公布过一份机器可读的列表，所以条码来自收藏者在 [wikiwiki.jp](https://wikiwiki.jp/barcode/) 上输入他们所拥有卡片的那些页面。每个条目都保留它那一页的地址。五个条目没通过它们自己的校验位，意味着有人打错了一个数字。同样那些页面给出每张卡片的数字，而五个之中有四个只有一种单个数字的修复能在卡片自己的机器上读成那些数字，所以那四个以修复后的数字打印。第五个，ガングラティ，被列为一名敌人，其 13 个数字拼出它的数字而非一个条码，其 39600 的 HP 是没有条码能给出的：高于 20000 时机器只以 900 结尾的步长读取 HP。它以 3996666425073 打印，读作它的其他数字和 HP 39900，最接近的那个。每张卡片上印的数字都由本项目的解码器从条码读出，而非从 wiki 复制。

有六个列表是为第一代条码战士而写的：原始套组、恶魔军团 God Mars 登场、酎拳 Khan 反击、最终决战：神对母亲、糖果卡，以及快乐快乐月刊的小绅士卡，它们说自己配条码战士而非 II。四个用第一代设备的表来描述标志；God Mars 列表不打印数字，而且它没有魔法师、也没有草药或魔法道具，那些只有 II 才读。正伝3 和正伝4 列表需要条码战士 II Double 的 7 读，正伝4 的卡片有一半用到它。其余 24 个以 II 的打印。

塞尔达、小学二年生杂志和街头霸王 II 的卡片来自 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的 `deeta.js` 中的卡片列表，它以英语发布它们，所以那些卡片带英文名。一件塞尔达道具，红药水，也是 II 棋盘游戏的一张卡片。

Dragon Slayer、哆啦A梦：大雄的恐龙、小绅士和明治的卡片在任何地方都没有转录，所以它们的条码是一张一张从 [barcodebattler.co.uk 发布](https://www.barcodebattler.co.uk/scans/Japan/) 的卡片扫描上读出的，每一张都靠它正面印的数字系到它的名字上。只有编号 1 和 5 的明治卡被扫描过。

超级马力欧世界套组，以及 Irwin 在美国和加拿大、Tomy 在英国和欧洲卖的那些卡包，来自 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的卡片页面，那里把每个条码都打了出来。Tomy 的卡片是 Epoch 的代码换上本地名字，每个名字不同的版本各一个列表：英国、爱尔兰和意大利共用一个，而德国、西班牙和法国各自给一些道具改名。Irwin 的美国和加拿大卡片带同样的名字和代码，加拿大的那些在英文旁加法文，所以它们是一个列表。Irwin 改了全部十张道具和新闻卡的代码：九张读作同一件道具，而它的 Life Crystals，正面印「EP = ??」而非一个数字，读作 300，而 Epoch 的卡片打印并读作 1600。

Datach 龙珠 Z 附带 40 张卡片。它的 [说明书](https://setsumei.cloudfree.jp/famicom/datachdragonballz/datachdragonballz.html) 说其中一些，超级赛亚人悟空、超级赛亚人特兰克斯、最终形态弗利萨和完全体细胞在内，不带条码，并请玩家把自己的一个贴到那些上面。带条码的那 35 张，加上一张特别的超级赛亚人悟空卡，就是此处打印的 36 张，取自 [puNES](https://github.com/punesemu/puNES) 模拟器源码里的列表，每一张在加入前都由 MAME 中的游戏读过。

游戏只有当一个条码的条、以及它的空格，至少来三种不同的宽度时才读取它；它在 $B085 处的程序里把它测到的宽度分类，并拒绝一个宽度种类更少的扫描。一个三种宽度为 1、2 和 4 的代码只在某些刷卡速度下读取。本程序为游戏建的每个代码在任何速度下都能读取，`maeyomi decode --device dbz` 会命名一个游戏拒绝的代码，而超市会标出它读不了的商品。

Datach 奥特曼俱乐部附带 40 张卡片，其中两张空白。其余 38 张是 [retrostuff.org](https://retrostuff.org/2019/03/23/bandai-datach-ultraman-club-spokon-fight-barcodes-for-mame/) 从一套盒装读出的代码，按 puNES 列表命名它们的方式命名，每一张都由 MAME 中的游戏读过。后来的 Datach 游戏不像龙珠 Z 那样拒绝一个代码：它们会读取条只来两种宽度的代码。它们共同的麻烦是一个条或空格恰好为 1、2 和 4 个模块宽的代码，它只在某些刷卡速度下读取；发售的奥特曼俱乐部卡片中有五张是这样的代码。本程序为一款 Datach 游戏建的每一张卡片都避开它们。

SD 高达大战附带 40 张卡片。其中 37 张带两个条码，底边一架机动战士、顶边一张指令卡，而一张特别卡各带一个：76 个条码，是 [retrostuff.org](https://retrostuff.org/2019/05/12/bandai-datach-sd-gundam-gundam-wars-barcodes-for-mame/) 从一套盒装读出、与 puNES 列表相符、每一个都由 MAME 中的游戏读过的。

幽游白书附带 40 张卡片，其中三张没有条码。其余 37 张来自 [archive.org](https://archive.org/details/yu-yu-hakusho-bakuto-ankoku-bujutsue-box-front) 在它一套完整卡片的扫描旁所存的电子表格，按那份表格命名它们的方式命名，每一张都由 MAME 中的游戏读过。

J 联赛超级顶级球员附带 40 张卡片，每张带四个条码，一家俱乐部和三名球员或四名球员。那 160 个条码来自 [archive.org](https://archive.org/details/j-league-super-top-players-manual) 在它一套完整卡片的扫描旁所存的电子表格，按游戏自己的球员名录命名它们的方式命名，每一个都由 MAME 中的游戏读过。

Barcode World 附带 24 张卡片和一张空白的白卡。它们的条码是从 [barcodebattler.co.uk 发布](https://www.barcodebattler.co.uk/scans/Japan/BarcodeWorld/) 的卡片扫描上读出的，按卡片所印命名，每一个都由 MAME 中的游戏读过。它的武器、护具和道具是在战斗中而非在角色画面扫描的，所以它们原样打印、不带数字。

Barcode Battler 战记附带 10 张卡片：5 张角色、3 张道具和 2 张空白白卡，据 [它的日文维基百科条目](https://ja.wikipedia.org/wiki/%E3%83%90%E3%83%BC%E3%82%B3%E3%83%BC%E3%83%89%E3%83%90%E3%83%88%E3%83%A9%E3%83%BC%E6%88%A6%E8%A8%98_%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E6%88%A6%E5%A3%AB%E5%87%BA%E6%92%83%E3%81%9B%E3%82%88!)。无人公布过它们的条码，所以 `maeyomi official --device senki` 会这么说，而不是打印一张空白整版。没有记录说 Lupin III、Donald Duck、Spider-Man、Alice no Paint Adventure、三款哆啦A梦游戏或 Dragon Slayer II 附带卡片，而前四款的说明书也没命名任何一张。Dragon Slayer II 已知会读的那一张卡片，来自条码战士 II 套组的 Selios，列在那款游戏下。

已知有十张 Battle Space 卡片和八个 Monster Maker 条码。这些条码来自 [GBE+ 模拟器的 Barcode Boy 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/Barcode_Boy.txt)，它从高分辨率扫描列出每一张已知的 Barcode Boy 卡片，以及另外两个 Monster Maker 代码，其第一张卡片正面的 Link 和 Lufia，来自 [MAME 的 Game Boy 软件列表](https://github.com/mamedev/mame/blob/master/hash/gameboy.xml)。Monster Maker 附带五张卡片，其中两张各带四个条码。每张 Battle Space 卡片解码为它上面印的职业，每张 Monster Maker 卡片解码为它所命名的英雄。其中两名英雄按游戏显示的样子命名，エルサイス 和 ハーゲン，而笔记写作 エリサイス 和 ハーグン。

Kattobi Road 附带六张卡片，而 [MAME 的 Game Boy 软件列表](https://github.com/mamedev/mame/blob/master/hash/gameboy.xml) 给出全部六个条码，其中有 GBE+ 笔记所缺的方程式赛车那张。每一张解码为它所命名的车，其中两张按游戏显示的样子命名，ナイター2000 和 ハイスラックス，而笔记写作 ナイト 2000 和 リイスラックス。

Famista 3 附带四张卡片，列在 MAME 软件列表给它们的名字下，每一张读作它所命名的种类：三名打者和一名投手。

Family Jockey 2 附带八张卡片：两匹赛马、三匹母马和三匹种马，列在 MAME 软件列表给它们的名字下。GBE+ 的笔记发现其中五张给出的数字与卡片上印的不同，而这些卡片打印游戏所读取的。

Card de Asobu 附带 46 张卡片，列在 GBE+ 的 HCV-1000 笔记给它们的名字下。其中三个名字不可能属于它们的假名，已予修正：ぬ 的卡片是 ぬいぐるみ，ら 的是 らっぱ，而 しょうぼうしゃ 和 むぎわらぼうし 用 ぼう 拼写。游戏在 GBE+ 中读过它们中的每一张。

Oshare Majo 的卡片是 Love and Berry 街机卡片，而除了 GBE+ 笔记里的六个，它们代码的列表从未公布过。游戏为它能被给的每一张卡片保留一张图像，按物品的代码命名，所以此处的 281 张卡片就是那些图像，各以一个游戏自己的解码器读作那件物品的代码打印。

Mushiking 的卡片是游戏保存在它自己列表里的街机卡片，535 个代码，各按游戏存储它的样子打印；一张以 FFF 结尾的卡片以 FFF 打印，游戏把它读作卡片自己的版本。

Wantame 的卡片是游戏保存在它自己表里的街机卡片，235 个代码，各按游戏存储它的样子打印。GBE+ 的笔记说街机游戏一直到 2009 年都在出新卡片，所以有些街机卡片在 DS 上读不了；这里只有 DS 游戏接受的那些。

Rockman 的 Wave Card 是 GBE+ 的 Wave Scanner 笔记里 211 个不同的代码，以每张 Wave Card 都带的 040000 打印。笔记里有五个条码的前六位数被调换了位置，这不改变扫描器送出的任何东西。

电车大集合的卡片是 [MAME 的 Beena 软件列表](https://github.com/mamedev/mame/blob/master/hash/sega_beena_cart.xml) 连同它们的值一起给出的 50 列电车和那张测试卡。从那个列表里的扫描读出，扫过的每张卡片的条都拼出 MAME 为它所列的值。面包超人 ABC 的 50 张卡片和测试卡来自同一个列表，按它们的扫描所印命名。TV Ocha-Ken 的 50 张卡片来自 [MAME 的 TV Ocha-Ken 软件列表](https://github.com/mamedev/mame/blob/master/hash/tvochken.xml)，按它的扫描所印命名，而每张扫描的条都拼出 MAME 为那张卡所列的值。

Epoch 为 Excite Stage '94 给 1994 年 J 联赛的 12 家俱乐部各印了一张名单卡。它们的条码是从 [barcodebattler.co.uk 发布](https://www.barcodebattler.co.uk/scans/Japan/J-League/) 的扫描上读出的，而 Excite Stage '94 和 '95 都把每一张读作一张道具卡，已在 MAME 中核对。

## 作弊码

除九个之外，每台主机和每款游戏都提供一种或多种作弊卡，每一种都把它所命名的每个数字设在设备所接受的最大值。`maeyomi cheat --device famista3 --kinds` 列出一个设备的种类，`--kind era` 打印一种，而网页在 **作弊** 标签页提供它们，该标签页把每一种一起或一次一种地显示和打印。第一种是默认，也就是本节为每个设备所描述的那张卡片。

默认种类的卡片名为 Maximus Cheatimus，其余的按它们的种类命名，如 Most power。`--name`，或页面上的名称字段，给某一种起一个你自己的名字；每一种一起时会按种类各保留一个名字，所以整版绝不会在每张卡片上重复同一个名字。凡是只显示一张卡片的地方，页面都单独显示那张卡片而非一整版。

| 主机或游戏 | 种类 |
|---|---|
| Barcode Battler II | `fighter`、能持有每件道具的 `warrior`、`items` |
| First Barcode Battler、Double、Datach Dragon Ball Z | `fighter`、`items` |
| Datach Ultraman Club | `strongest`、`items` |
| Datach SD Gundam Wars | `strongest`、`hp`、`ap`、`dp` |
| Datach Yu Yu Hakusho | `strongest`、处于最高等级的 `items` |
| Datach Battle Rush | `strongest`、`attack`、`defense`、`speed` |
| Barcode World、Barcode Battler Senki、Hatayama Hatch | `strongest`、`warrior` |
| Lupin III、Donald Duck、Spider-Man、Alice、三款哆啦A梦游戏、Dragon Slayer II | `strongest`，然后为其他每个效果各一种 |
| J.League Excite Stage '95 | `strongest`、`items` |
| J.League Excite Stage '94 | `strongest`、`keeper`、`items` |
| Battle Space | `strongest`、`dp`、`mp` |
| Monster Maker | `strongest`、游戏后期的 `ap` 和 `mp` |
| Kattobi Road | `strongest`、`torque` |
| Famista 3 | `strongest`、`average`、`speed`、`era`、`pitch`、`stamina` |
| Family Jockey 2 | `strongest`、`mare`、`stallion`、给一个南梦宫盒子奖励落下后能达到 10 的那匹马的 `boxed` |
| Barcode Taisen Bardigun | `strongest`、`power`、`smarts`、`speed` |

一种会再次打印最强卡片的种类会被略去，所以 Battle Space 没有 HP 或 AP 种类：它的最强卡片已经两者都最多。Datach J 联赛超级顶级球员一种也没有：它的卡片命名球员，而游戏的程序为每位球员保留一份档案、一张脸和一个外观，却没有一个卡片能提升的数字。Card de Asobu、Oshare Majo、Mushiking、Wantame、Rockman、电车大集合、面包超人 ABC 和 TV Ocha-Ken 也一种都没有：一张卡片命名一个假名、一件物品、一只甲虫、一个招式、一只狗、一件服装、一张战斗卡、一列电车、一个字母或一件给 Ocha-Ken 做的事，别无它物。

`maeyomi cheat -o cheat.pdf`，或者网页的 **作弊** 标签页，在页面任意处输入上、上、下、下、左、右、左、右、B、A 也会打开它。这张卡片是一名机械魔法师，99900 生命，攻击翻倍。设备显示 14600 攻击和 19900 防御，而以 24600 攻击作战。

关于它没有任何东西是写死的。生成器把每一名满血的正面读取战士走一遍解码器自己的运算，并留下那个以攻击和防御合计作战最多的，避开每个未解决的分支。那隐藏的 24600 是设备自己的：一名机械战士，生命高于 20000 且攻击数字为 46，会获得一个显示从不展示的加成。据 [barcodebattler.net](https://barcodebattler.net/page21.htm)，有人见过一台设备用代码 4994699095453 恰好这么做。卡片把那个隐藏值印在它的特殊能力旁边。

`maeyomi cheat --items -o cheat.pdf` 加上五件处于它们数字所能容纳的最大值的道具：一件 9900 攻击的武器、一件 9900 防御的护甲、一瓶 99900 生命的药水、99 份草药和 99 魔法点。每一件都把一种不同的、有记载的力量传给使用它的人：对手防御削 80%、自己防御加一半、对手生命减半、对手攻击减半、对手特殊能力作废。几件道具的力量是否叠加没有记载，所以这一切都不依赖于它。

命令会说明哪些工作能用每件道具，取自 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5) 里的装备表。没有魔法师能持有武器或护甲，所以刀刃和盾牌是给任何工作的战士的，而药水、草药和水晶都对作弊魔法师有效。

`maeyomi cheat --device bb1 --items -o cheat.pdf` 为第一代条码战士做同样的事：一名每个数字都在其上限的战士，19900 生命、9900 攻击和 9900 防御，攻击翻倍，外加处于上限的一件武器、一件护甲和一瓶药水。战士是工作 9，那个设备让它装备每件武器，并给 0 到 4 类武器多一半的攻击。

`maeyomi cheat --device double --items -o cheat.pdf` 是三者中最强的：一张 Double 卡片，99900 攻击和 99900 防御，即那个出处所述的上限，以及那个把对手生命减半的力量。那个力量是生命的两个数字，所以它留下 92900 生命。道具是 II 的，各带 Double 自己表里的一种力量。Double 没有装备表被公布过，所以命令不说哪个工作能用哪件道具。

`maeyomi cheat --device dbz --items -o cheat.pdf` 是处于必杀技等级 3 的超级赛亚人悟空，99500 HP、48250 BP 和 33250 DP。HP 是游戏规则所能容纳的最大值；BP 和 DP 是其条码仍能出成十个十进制数字的最强一对，由在每张可打印卡片上搜索找出。那比游戏藏在它自己程序里的那张卡多十倍有余。道具是每种最强效果各一个：仙豆、神龙、神、古鲁、超神水，以及等级 4 的 Porunga。

`maeyomi cheat --device ultraman -o cheat.pdf` 是奥特曼，PW、ST 和 SP 全在 9900，即游戏两张表所能加到的最大值。

`maeyomi cheat --device sdgundam -o cheat.pdf` 是 Quin Mantha，HP、AP 和 DP 合计最多的机动战士，每个加成都在它的顶点：HP 7700、AP 7000、DP 9000 和 CP 6。

`maeyomi cheat --device yuyu -o cheat.pdf` 是游戏藏起的那名斗士，SP 户愚吕，9999 HP、9999 SP 和他全部四种招式。游戏为一串确切的比特给出它，而万代印的卡片没有一张带有。

`maeyomi cheat --device barcodeworld -o cheat.pdf` 是一名工作 9 的魔法师，HP 49900、ST 19900、DF 19900、10 魔法和 5 草药，每个数字都在游戏所读取的最大值。`maeyomi cheat --device senki -o cheat.pdf` 是给 Barcode Battler 战记的同一名魔法师。

四款密码画面的游戏各得它最有用的效果：Lupin III 的无伤、Donald Duck 的带每种力量和 12 颗心的天空关卡、Spider-Man 的无限命，以及 Alice no Paint Adventure 中设好每个后期标志的故事最后一幕。Spider-Man 把它的三个效果分别放在不同地方，所以无限命、双倍生命和 Boss 生命减半可以一个接一个地刷，三者都保留。

哆啦A梦 2 得 99 条命，哆啦A梦 3 从第 5 世界开始，而大雄与妖精之国让哆啦A梦无敌。

J 联赛 Excite Stage '95 得整体能力提升 253，是任何卡片对它的最大提升。

Dragon Slayer II 以每项状态都在最高开始。

Battle Space 得一名 Sorcerer King，拥有每个法术的职业，HP 999900、AP 99900、DP 99400 和 MP 83100。没有代码能把四项都读到它们的顶点：MP 和 AP 在 999 会固定六个数字，而 HP 在 9999 需要它们自己用。

Monster Maker 得 Lorian，他在游戏后期以 9 级回归，HP 460，是任何英雄所达的最多，AP 和 DP 97。

Kattobi Road 得 USAドロンコ，一辆特殊车，11028 PS 和 403.4 kg-m 扭矩，是任何代码所给的最大马力。

Famista 3 得一名左打、打 60 支本垒打的新秀，是任何代码所给的最多，打击率 .204。

Family Jockey 2 得一匹六个数字全是 9 的赛马。

Barcode Taisen Bardigun 得 オマメ，Omame，它孵出时 HP 105，是任何 Barloid 最多的，强韧 7。它的其他种类孵出力量、智慧或速度最多的 Barloid；强韧没有自己的种类，因为 Omame 已经最多。

Hatayama Hatch 得一名法师，体力 99900、攻击和防御 19900、99 魔法。

Datach Battle Rush 打印攻击、防御和速度 233 的机器人那一对，是它们合计所达的最多，恢复 255。一个字节在游戏的求和里回绕，所以最大的部件并不造出最强的机器人。

J 联赛 Excite Stage '94 得 Gamamoto Kunikuni，那名各项都被评为 A 的隐藏球员。

## 两种语言和图画

每张卡片都用英语和日语印刷，无论页面是哪种语言，对每台主机和每款游戏都一样。在一张条码战士 II 卡片上，生物的种类、它如何作战、三个战斗数字、特殊能力和刷卡说明全都以两种语言出现。每个事实还有一张给尚读不懂任何一种语言的孩子看的图画：一条带生物种类图标的彩色带，一颗心、一把剑和一面盾代表数字，以及一个特殊能力图标，显示它改变什么、往哪个方向，如一把带向上箭头的剑表示「自身攻击翻倍」。箭头的方向承载含义，绝不靠它的颜色。给任何其他游戏的卡片带着那款游戏所读取的数字，其标签以两种语言、在同样的彩色图块上。一个游戏只用假名显示的名字，如一名 J 联赛 Excite Stage '94 球员、一名 Datach Battle Rush 驾驶员或一辆 Kattobi Road 赛车，会按规则为英文一侧罗马化。页面在它的语言改变时重绘每条消息和每个列表。

条码战士 II 的特殊能力文字是两种语言的公布措辞：日语抄自 barcodebattler.net/page05.htm，英语是本项目对同一页的读解。种族、职业和数值名称是本项目自己的翻译，用一名年幼读者最先学的平假名和片假名。一名玩家所选的名字按输入原样打印，用任一种文字。

网页用顶部的按钮在英语和日语之间切换，并记住这个选择。

日语以每个 PDF 阅读器都带、但以引用而非嵌入方式使用的字体排版。对一家印刷店，改送页面图像而非 PDF，`--images png`，它们是 600 dpi、字样已经画好的。

## 不用鼠标或看不见时怎么用它

页面只用键盘就能操作。一个跳转链接跳过报头，六个标签页是一站、用方向键在它们之间移动，Home 和 End 去到两端，每个控件都画出一个可见的焦点环，每个控件至少 44 乘 44 像素，而食品列表可以用键盘滚动。语言切换改变文档上的 `lang`，所以屏幕阅读器随它改变嗓音。当系统要求减少动画时，动画会被去掉。

axe-core 在六个标签页中的任何一个上、在浅色方案和深色方案中，对照 WCAG 2.2 A 和 AA 以及它自己的最佳实践集，都不报告任何违规。规则集无法做的那些检查是在一个真实浏览器里手工做的：焦点环是从获得焦点的元素读回的，而非从样式表。

PDF 带着一个没有结构树的 PDF 所能带的东西。每一个都为自己命名，所以阅读器会念「Barcode Battler II card: Tea」而非 `sheet.pdf`，并被告知优先用那个标题而非文件名。文档声明它的语言、它的作者和它是什么。卡片上的每个字都是真正的文本：名字、数字、特殊能力、两种语言，以及条下的数字，全都以一个人会读的顺序从文件里出来，先种类，再名字，再每个数字跟在说明它度量什么的标签之后，再特殊能力，最后是条码。

不在那里的东西：ReportLab 不发出标签树，所以这些不是 PDF/UA 文件。没有标题、没有列表、没有图标的替代文本，日语段落也没有被单独标记为日语。图标重复它们旁边的字已经说过的话，所以它们没有描述并不损失什么。一个验证器会把这些叫作未加标签。

## 颜色

卡片送到商业印刷者那里，这往往意味着活件以黑白运行，而且它们交到孩子手里，大约每十二个男孩里有一个分不清红和绿。两种情况都靠测量来处理。

没有一样东西仅靠颜色来区分。每条带都带它自己的名字和它自己的图标，而每个战斗数字都带它自己的形状和它的两字母标签，所以一张以灰度打印的卡片仍然说出了它在颜色里说过的一切。

[`colour.py`](src/maeyomi/rendering/colour.py) 带着运算，而 [`test_palette.py`](tests/rendering/test_palette.py) 把调色板约束到它：

| 检查 | 阈值 | 出处 |
|---|---|---|
| 一条带上的白字，在颜色和灰度中 | 4.5 比 1 | WCAG 2.2，对比度最小值 |
| 一个图标对它的图块，在颜色和灰度中 | 3 比 1 | WCAG 2.2，非文本对比度 |
| 两条战士带，在正常视觉下以及在红色盲、绿色盲和蓝色盲下 | 20 个 CIE 1976 单位 | 两种颜色读作两种不同颜色、而非一种颜色两种深浅的距离 |
| 两条以灰度打印的战士带 | 1.15 比 1 | 一个可见的色调级差 |
| 一件武器或护甲的一次性和永久变体，在灰度中 | 1.5 比 1 | 它们共用一个图标，所以色调得多承载一些 |

二色觉模拟是 Brettel、Vienot 和 Mollon 的线性近似。一版还会被光栅化、转成灰度，并把它上面的每个条码都解码出来，使这次打印在完全没有颜色的打印机那里也活下来。

## 出处

解码器是 [Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator) 中 `src/BarcodeRead.as` 的一个移植，该模拟器以 MIT 许可。属性区间、读取类型规则和能力表来自 [barcodebattler.net](https://barcodebattler.net/)。卡片夹具来自 [wikiwiki.jp](https://wikiwiki.jp/barcode/) 上的卡片列表，每个条目都记录了出处页面和抓取日期。每个来源、从它取了什么以及在哪种许可下：

- **[Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator)**，作者 finalfighter，MIT。[`src/maeyomi/decoder/`](src/maeyomi/decoder) 里的解码器移植了它的 `src/BarcodeRead.as`，而测试语料 [`tests/fixtures/simulator_corpus.json`](tests/fixtures/simulator_corpus.json) 来自它的卡片列表。
- **[barcodebattler.net](https://barcodebattler.net/)**，yuko2ch.net 的一个镜像，以及其作者在一台设备上测试过打印代码的 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)：属性区间、读取类型规则、能力表、高生命加成、工作 6 的裁定以及 Double 的 7 读。仅取事实。
- **[wikiwiki.jp](https://wikiwiki.jp/barcode/)**：日文卡片列表，每个条目都保留页面和地址。
- **[barcodebattler.co.uk](https://www.barcodebattler.co.uk/)**：来自它 `deeta.js` 的塞尔达、小学二年生和街头霸王 II 列表；来自它卡片页面的超级马力欧世界、Irwin 和 Tomy 列表；条码战士 II 的技术笔记；以及 Dragon Slayer、哆啦A梦、小绅士、明治、Barcode World 和 J 联赛俱乐部条码所读自的卡片扫描。仅取事实；它的代码没有一行出现在这里。
- **[puNES](https://github.com/punesemu/puNES)**，GPL-2：36 张 Datach 龙珠 Z 卡片的条码和名字，每一张都由游戏本身核对过。puNES 的代码没有出现在这里。
- **[retrostuff.org](https://retrostuff.org/)** 和 **[archive.org](https://archive.org/)**：奥特曼俱乐部、SD 高达大战、幽游白书和 J 联赛超级顶级球员的条码。
- **[一个 5ch 帖子](https://mevius.5ch.net/test/read.cgi/toy/1226667612/)**，第 484 楼：Double 的 7 读种族。
- **[GBE+](https://github.com/shonumi/gbe-plus)**，GPL-2：它的 [Barcode Boy 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/Barcode_Boy.txt) 给出读取器的协议和每一张已知 Barcode Boy 卡片的条码。GBE+ 的代码没有出现在这里。
- **[MAME 的 Game Boy 软件列表](https://github.com/mamedev/mame/blob/master/hash/gameboy.xml)**：Kattobi Road、Famista 3 和 Family Jockey 2 卡片的条码和名字。
- **GBE+ 的 [Bardigun 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/Barcode_Taisen_Bardigun.txt)**：Bardigun 读取器的协议和九个条码连同它们孵出什么，每一个都在此处的 MAME 中核对过。
- **GBE+ 的 [HCV-1000 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/HCV_1000.txt)**：HCV-1000 的寄存器、46 张 Card de Asobu 卡片连同它们的名字，以及六张 Oshare Majo 卡片。GBE+ 本身，GPL-2，在这些核对中运行 Card de Asobu，由 [`tools/oracle/gbe_plus/build.sh`](tools/oracle/gbe_plus/build.sh) 打补丁；它的代码没有一行随包发行。
- **GBE+ 的 [Wave Scanner 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/Wave_Scanner.txt)**：Wave Scanner 的布局和 214 张 Wave Card 连同它们的编号、条码以及英语和日语名字，这些由 Rockman 打印。
- **GBE+ 的 [Wantame Card Scanner 笔记](https://github.com/shonumi/gbe-plus/blob/master/src/docs/technical/Wantame_Card_Scanner.txt)**：扫描器如何通过麦克风送出一张卡片的代码和校验和。
- **[Unicorn](https://www.unicorn-engine.org/)**，GPL-2，在这些核对中运行 Oshare Majo 自己的卡片解码器、Mushiking 自己的卡片比较和 Wantame 自己的卡片核对；它不是包的依赖。
- **[MAME 的 Beena 软件列表](https://github.com/mamedev/mame/blob/master/hash/sega_beena_cart.xml)**，在 MAME 0.289 中：电车大集合和面包超人 ABC 的卡片连同它们的值，以及条纹布局和面包超人名字所读自的卡片扫描。
- **[MAME 的 TV Ocha-Ken 软件列表](https://github.com/mamedev/mame/blob/master/hash/tvochken.xml)**，在 MAME 0.289 中：TV Ocha-Ken 的卡片连同它们的值，以及它的条纹布局和卡片名字所读自的卡片扫描。
- **[MAME](https://www.mamedev.org/)** 0.289 在这些核对中运行每一款游戏。游戏规则来自每款游戏自己的程序；没有一个 ROM 字节被发行，而每个 ROM 都在 [`artifacts.manifest.json`](artifacts.manifest.json) 里以它的校验和命名。
- **[Open Food Facts](https://world.openfoodfacts.org/)**，Open Database License 1.0：[`src/maeyomi/products/japan.json`](src/maeyomi/products/japan.json) 里的条码、产品名和品牌，一个保持在 [同一许可](https://opendatacommons.org/licenses/odbl/1-0/) 下的子集。在线查找在它的 user agent 里命名本项目，正如它们的条款所要求。
- **VITIMan/barcode-battler-engine**，GPL-3，未被使用：没有代码、结构或命名来自它。它只是指向了此处直接抓取的 wikiwiki.jp 列表。

在来源有分歧的地方，问题记录在 [`src/maeyomi/decoder/uncertainties.py`](src/maeyomi/decoder/uncertainties.py) 里，连同每个来源怎么说以及选了什么。解码器遵循模拟器，除非在一台设备上测试过打印代码的来源另有说法：高生命加成遵循 [barcodebattler.net](https://barcodebattler.net/page21.htm) 和一份 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)，而工作 6 是战士。所记录的问题中有五个会把一个未经验证的值放到一张打印出的卡片上，而生成器拒绝发出任何到达它们的代码。
