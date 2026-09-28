<div align="center">

# maeyomi

<strong>为 Barcode Battler 系列机器和条形码游戏打印能玩的卡片。</strong>

[English](README.md) &nbsp;|&nbsp; [日本語](README.ja.md) &nbsp;|&nbsp; 简体中文 &nbsp;|&nbsp; [香港繁體中文](README.zh-Hant-HK.md)

[![ci](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml/badge.svg)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.14-blue)](pyproject.toml)

<p align="center">
  <a href="#安装">安装</a> &nbsp;|&nbsp;
  <a href="#启动">启动</a> &nbsp;|&nbsp;
  <a href="#命令行">命令行</a> &nbsp;|&nbsp;
  <a href="#工作原理">工作原理</a> &nbsp;|&nbsp;
  <a href="#超市">超市</a> &nbsp;|&nbsp;
  <a href="#来源">来源</a>
</p>

</div>

已录入 **1544** 张官方卡片。**2958** 种日本食品。**100** 种特殊能力。卡片可用英文、日文或中文打印。测试覆盖率 **100%**。Barcode Battler II 的卡片已在实机上验证。

---

Barcode Battler II 读取条形码，仅凭其中的数字推导出一个角色或一件道具。Maeyomi 是这台机器自己对正面读取的称呼，也就是产生角色的那种读法。本程序把这套运算反过来：想要一张防御 2400 的护甲卡片，它就算出机器会以这种方式读取的条形码，然后打印出来。

每个条形码在印到纸上之前都会重新解码一次，每一页打印稿都会被栅格化，再用条形码阅读器读回。打印出的卡片已在一台实体 Barcode Battler II 上刷过。

1991 年的第一代 Barcode Battler 以自己的方式读取同样的数字：每个角色都是战士，体力上限为 19900，攻击和防御上限为 9900，两位数代码是另一张表中的标志，因此 18 在这里代表主角，而在 II 上则是攻击翻倍。给 `decode`、`generate` 和 `cheat` 加上 `--device bb1`，即可为它制作卡片。它的解码器能复现为它编写的四份清单中已公布的 113 张卡片，但目前还没有任何一张为它制作的卡片在实体的第一代 Barcode Battler 上读取过，为它生成的每一页都注明了这一点。

Barcode Battler II Double，即 1993 年的 II²，没有读取器，从 II 接收代码。它按 II 的方式读取，唯一的例外是以 7 开头且第十位为 8 的代码，它用自己的方式读取：攻击和防御可达 99900，特殊能力取自体力的两位数字。`--device double` 可为它制作卡片，依据的是 [barcodebattler.net](https://barcodebattler.net/bb2c0.html) 上的 "BBIIダブルC0"。这种读法解释了 正伝3 清单中无论哪种 II 读法都无法解释的十一张卡片。它的种族是攻击的百位数减 5，这是一份[收藏者的报告](https://mevius.5ch.net/test/read.cgi/toy/1226667612/)在 正伝3 和 正伝4 的敌方卡片上发现的；十一张全部吻合，而百位数小于 5 时种族未知。它的速度仍然未知。Double 还指定了两个 II 所没有的类别：职业 4 对应僧侣，职业 6 对应圣战士，并且有它自己的特殊能力表。

Bandai 的 Datach Dragon Ball Z: Gekitou Tenkaichi Budoukai 是 1992 年的一款 Famicom 游戏，附带一台条形码读取器。`--device dbz` 可为它制作卡片。该游戏把十位数字的各个比特打散到一个 40 位的数中，从中读出一个角色或一件道具、必杀技等级、HP、BP 和 DP。这条规则是从游戏自身的程序中读出的，解码器与在 MAME 中运行的游戏在该游戏接受的全部 232 个代码上结果一致。用 `--character` 选择角色或道具，可以用游戏显示的名称，也可以用其 id；用 `--level` 选择等级，用 `--hp`、`--bp` 和 `--dp` 指定数值；当这些精确数值无法打印时，加上 `--nearest` 以取得最接近的可打印卡片；数值足够高的角色会变为更强的形态，与游戏中一样。目前还没有任何一张为它制作的卡片被实体 Datach 读取过，为它生成的每一页都注明了这一点。

Datach Ultraman Club: Supokon Fight! 是 Bandai 的第二款 Datach 游戏，发行于 1993 年。它把条形码读成 51 种类型之一，0 到 27 是奥特英雄和怪兽，32 及以上是道具，再读出它称为 PW、ST 和 SP 的三个数值，每个从 0 到 9900，步长为 100。`--device ultraman` 可为它制作卡片：用 `--character` 选择类型，可以用游戏显示的名称或编号；用 `--hp`、`--st` 和 `--df` 按此顺序指定三个数值。该范围内的每个值都能打印。这条规则是从游戏程序中读出的，并与在 MAME 中运行的游戏本身在其 38 张已发行卡片以及每种类型各构造一个的 51 个代码上结果一致。目前还没有任何一张为它制作的卡片被实体 Datach 读取过。

Datach SD Gundam: Gundam Wars 同样发行于 1993 年，它把条形码读成 63 台机动战士之一或 59 张指令卡之一。机动战士以自身的 HP、AP、DP 和 CP 为基础，各自加上一张表中的加成，并携带两种近程武器之一和两种远程武器之一；指令卡携带其效果及所消耗的 CP。`--device sdgundam` 可为它制作卡片：用 `--character` 按名称、型号或编号选择卡片，用 `--hp`、`--st` 和 `--df` 指定数值，它们分别对应 HP、AP 和 DP，并用 `--pick sr=1`、`--pick lr=5` 或 `--pick cp=11` 指定武器和 CP。介于游戏可容纳的两个值之间的数会变成最接近的那个，命令会说明这一点。这条规则与 MAME 中的游戏在其 76 个已发行条形码以及每个槽位各构造一个的 122 个代码上结果一致。目前还没有任何一张为它制作的卡片被实体 Datach 读取过。

Datach Yu Yu Hakusho: Bakutou Ankoku Bujutsukai 同样发行于 1993 年，它把条形码读成 22 名角色或 10 件道具之一，另外还有一名游戏隐藏的角色。角色的 HP 和 SP 是其固有的，任何条形码都不会改变它们；条形码决定的是它的四个招式中哪些可以使用。道具按四个等级之一增加 HP 或 SP，或者改变对战模式的一条规则。`--device yuyu` 可为它制作卡片：用 `--character` 选择卡片，用 `--pick moves=15` 选择招式，每个招式占一个比特，用 `--pick level=3` 选择道具的等级。这条规则与 MAME 中的游戏在其 37 张已发行卡片以及覆盖所有角色、掩码和道具构造的 183 个代码上结果一致。目前还没有任何一张为它制作的卡片被实体 Datach 读取过。

1994 年的 Datach J.League Super Top Players 把条形码读成 1993 年 J.League 十家俱乐部的 150 名球员之一，或读成这些俱乐部之一。一张卡片指定一名真实球员，本身不带任何数值，因此每名球员的能力由游戏保存，也就没有为它准备的秘籍卡片。`--device jleague` 可为它制作卡片：用 `--character` 按名称或编号选择球员或俱乐部。这条规则与 MAME 中的游戏在其 160 个已发行条形码以及为覆盖游戏允许的每个折叠值而构造的 12 个代码上结果一致。目前还没有任何一张为它制作的卡片被实体 Datach 读取过。

Datach 游戏 Crayon Shin-chan: Ora to Poi Poi 的程序中完全没有读取条形码的代码，因此无法接受卡片。

Datach Battle Rush: Build Up Robot Tournament 在其 Robo Factory 中用按顺序扫描的两张卡片组装一台机器人，`--device battlerush` 可制作这一对卡片。第一张卡片携带机器人的编号、头部、躯干、肩部、脚部和驾驶员；第二张携带武器和四个等级。游戏故意拒绝商店商品的条形码：它自己卡片的最后一位比 EAN 应有的校验位小一或小二，因此这些卡片按这一位数字打印，普通条形码阅读器无法读取。用 `--character` 按编号或 16 名对手之一的名称选择机器人，用 `--pick head=3 --pick attack=7` 等选择部件和等级。这条规则是从游戏程序中读出的，并与 MAME 中的游戏在尝试过的每一对上结果一致；MAME 只部分模拟了游戏的存档芯片，因此检查时写入其中两个字节以进入工厂。目前不知道有 Bandai 所印卡片的清单。

Sunsoft 的 Barcode World 是 1992 年的一款 Famicom 游戏，它通过连接到 Famicom 的 Barcode Battler II 读取卡片，因此能读取任何条形码。`--device barcodeworld` 可为它制作卡片。该游戏读取数字的方式与 Barcode Battler II 大致相同，以百为单位：HP 最高 49900，ST 和 DF 最高 19900，其中体力超过 19900 需要百位为 9 且速度为 5，魔法和药草由职业决定。用 `--character` 选择战士或魔法师，用 `--hp`、`--st` 和 `--df` 指定数值，用 `--pick job=3`、`--pick speed=8` 和 `--pick ability=45` 指定职业、速度和能力。这条规则与 MAME 中的游戏在 211 个代码上结果一致，其中包括其 24 张已发行卡片，也与这里构造并尝试过的每一张卡片一致。

Epoch 的 Barcode Battler Senki 是 1993 年的一款 Super Famicom 游戏，它通过 Barcode Battler II Interface 上的 Barcode Battler II 读取卡片，`--device senki` 可为它制作卡片。它读取数字的方式与 Barcode World 相同，但有三处不同。8 位代码到达时前面带五个零，因为接口把 Barcode Battler II 的空格变成了零。从末端读取的道具会保留其强度中小于十的个位。而印在 Interface 自己包装盒上的代码在两种对战模式中都会打开声音测试，而不是生成一张卡片。这条规则与 MAME 中的游戏在 253 个代码上结果一致，其中包括这里构造并尝试过的每一张卡片。The Black Store 是剧情模式中的一家隐藏商店，它以较小的偏移量读取从末端读取的卡片，因此这类卡片还会显示该商店赋予它的 HP、ST 和 DF；这种读法与 MAME 中的游戏在 232 个代码上结果一致，这些代码是通过设置商店地图事件所设置的标志来到达的，而不是走到商店。MAME 0.289 把每位数字错开一个比特发送给 Super Famicom，因此检查通过一个专门为此编写的接口向游戏输入代码。

Epoch 另有四款 Super Famicom 游戏通过同一接口在密码画面读取代码，每个代码从一份固定清单中触发一种效果，而不是生成角色：Lupin III: Densetsu no Hihou o Oe! 使用 `--device lupin`，Donald Duck no Mahou no Boushi 使用 `--device donald`，Spider-Man: Lethal Foes 使用 `--device spiderman`，Alice no Paint Adventure 使用 `--device alice`。这些效果包括无伤、无限生命或道具全满之类的秘籍，跳转到某一关、某一章或某个结局，以及声音测试。`maeyomi kinds --device lupin` 列出一款游戏的效果，`--character` 按名称或编号选择其中之一。每条规则都是从游戏程序中读出的，并与 MAME 中的游戏在尝试过的每个代码上结果一致：Lupin III 为 250 个，Donald Duck 为 247 个，Spider-Man 为 221 个，Alice 为 253 个。不符合任何规则的代码会被读取，但什么也不做。

三款 Super Famicom 上的 Doraemon 游戏以同样的方式在各自的两个画面上读取代码：Doraemon 2 使用 `--device doraemon2`，在密码画面和关卡的道具菜单中读取；Doraemon 3 使用 `--device doraemon3`，在密码画面和游戏进行中的装备菜单中读取；Nobita to Yousei no Kuni 使用 `--device yousei`，在密码画面和城镇地图的道具画面中读取。密码画面提供无敌、99 条命或更靠后的世界之类的秘籍，菜单则提供秘密道具、武器、护具和道具。每张卡片都注明了应在哪个画面扫描。Doraemon 4 带有同样的读取代码，但从未调用它，因此其中没有任何画面接受条形码。

J.League Excite Stage '94 在季前赛之前，于名单画面的 Barcode Battler 面板上读取代码，`--device excite94` 可为它制作卡片。校验位为 4 或以上的代码是 240 名隐藏球员之一，每人有一个名字以及踢球、射门、跑动和盘带的评级，门将则是防守的评级；校验位更低的代码是道具卡，与 Excite Stage '95 的道具卡类似。用 `--character` 选择球员或道具，用 `--pick value=253` 指定道具的数量。名字和评级直接取自游戏自身的数据表，除了一名任何代码的数字都无法达到的球员外，其余球员都可以打印。PK 模式以同样的方式读取球员，但以自己的方式读取道具卡，读成六种 PK 道具类型之一以及 0 到 9 的等级，卡片上也会显示这些；每种 PK 类型在比赛中起什么作用尚未追查。两条规则都与 MAME 中的游戏在尝试过的每个代码上结果一致，其中 PK 模式为 168 个。

Super Famicom 上的 J.League Excite Stage '95 在公开赛、联赛、锦标赛或梦幻比赛之前，于其 Barcode Battler II 输入画面上读取代码，`--device excite95` 可为它制作卡片。每个代码都是一张道具卡：整体实力、盘带、传球速度、踢球速度或门将扑救，提升 0 到 253；或者是一张特殊卡，提供最多 4 点让分，或让犯规不出牌。用 `--character` 选择道具，用 `--pick value=253` 指定数量。这条规则与 MAME 中的游戏在尝试过的每个代码上结果一致。PK 模式以另一种方式读取代码，本项目未对其建模。

Falcom 的 Dragon Slayer: Eiyuu Densetsu II 由 Epoch 于 1993 年在 Super Famicom 上发行，它在标题菜单和野外菜单中读取代码，`--device dslayer2` 可为它制作卡片。标题菜单提供的秘籍包括所有状态达到最高、经验和金钱翻倍、怪物列表或声音模式。在野外，以 038438816 开头的代码会给出编号为其最后三位数字的道具，999 开启所有传送点，还有几个代码可以在未持有的情况下使用灯、Bisna 果实、休息蘑菇或地图。Epoch 为 Barcode Battler II 印制的 Dragon Slayer 卡片不会被游戏特殊对待。

Hatayama Hatch no Paro Yakyuu News! Jitsumei Ban 是 Epoch 1993 年的棒球游戏，它在其 Battle Baseball Board 上把代码读成一名对战者，`--device hatayama` 可为它制作卡片。按 Epoch 卡片的格式排列的代码会被原样读取：体力最高 99900，攻击和防御以百为单位最高 19900，巫师的魔法最高 99；其他任何代码则根据其最后几位数字计算。用 `--character` 选择战士或巫师，用 `--hp`、`--st` 和 `--df` 指定数值，用 `--pick mp=99` 指定魔法。同一代码的最后一位还会在游戏的另外两个条形码画面上选择一种战术和一幅图像，每张卡片都会印出选中的是哪一个。游戏附带 14 支球队的卡片，但没有人公开过它们的条形码。

## 支持的机器和游戏

下面的每台机器和每款游戏都对应命令行中的一个 `--device`，也对应网页上 **机器或游戏** 下的一个选项。这些机器、游戏及其卡包的照片可在 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/scans/Japan/) 上查看。

| 机器或游戏 | 日文名称 | 运行平台 | `--device` |
|---|---|---|---|
| Barcode Battler | バーコードバトラー | 独立主机 | `bb1` |
| Barcode Battler 2 | バーコードバトラー2 | 独立主机 | `bb2` |
| Barcode Battler 2 Double | バーコードバトラー2 ダブル | 独立主机 | `double` |
| Alice no Paint Adventure | アリスのペイントアドベンチャー | Super Famicom，经由 Barcode Battler II | `alice` |
| Barcode Battler Senki | バーコードバトラー戦記 | Super Famicom，经由 Barcode Battler II | `senki` |
| Donald Duck no Mahou no Boushi | ドナルドダックの魔法のぼうし | Super Famicom，经由 Barcode Battler II | `donald` |
| Doraemon 2 | ドラえもん2 のび太のトイズランド大冒険 | Super Famicom，经由 Barcode Battler II | `doraemon2` |
| Doraemon 3 | ドラえもん3 のび太と時の宝玉 | Super Famicom，经由 Barcode Battler II | `doraemon3` |
| Doraemon: Yousei no Kuni | ドラえもん のび太と妖精の国 | Super Famicom，经由 Barcode Battler II | `yousei` |
| Dragon Slayer II | ドラゴンスレイヤー英雄伝説II | Super Famicom，经由 Barcode Battler II | `dslayer2` |
| Hatayama Hatch | はた山ハッチのパロ野球ニュース!実名版 | Super Famicom，经由 Barcode Battler II | `hatayama` |
| J.League Excite Stage '94 | J.リーグエキサイトステージ'94 | Super Famicom，经由 Barcode Battler II | `excite94` |
| J.League Excite Stage '95 | J.リーグエキサイトステージ'95 | Super Famicom，经由 Barcode Battler II | `excite95` |
| Lupin III | ルパン三世 伝説の秘宝を追え! | Super Famicom，经由 Barcode Battler II | `lupin` |
| Spider-Man: Lethal Foes | スパイダーマン リーサルフォーズ | Super Famicom，经由 Barcode Battler II | `spiderman` |
| Datach Battle Rush | データック バトルラッシュ | Famicom Datach | `battlerush` |
| Datach Dragon Ball Z | データック ドラゴンボールZ | Famicom Datach | `dbz` |
| Datach J.League | データック Jリーグ スーパートッププレイヤーズ | Famicom Datach | `jleague` |
| Datach SD Gundam Wars | データック SDガンダム ガンダムウォーズ | Famicom Datach | `sdgundam` |
| Datach Ultraman Club | データック ウルトラマン倶楽部 | Famicom Datach | `ultraman` |
| Datach Yu Yu Hakusho | データック 幽遊白書 | Famicom Datach | `yuyu` |
| Barcode World | バーコードワールド | Famicom，经由 Barcode Battler II | `barcodeworld` |

## 安装

```bash
brew tap gufranco/maeyomi https://github.com/gufranco/maeyomi
brew install gufranco/maeyomi/maeyomi
```

这个 tap 就是本仓库。Homebrew 需要显式的 URL，因为本仓库的名称不是 `homebrew-maeyomi`，这样 formula、源代码和发布版本就放在一起，而不是放在另一个会逐渐不同步的仓库里。

安装时会拉取 Python 3.14，并根据已提交的锁文件构建一个隔离的环境，因此你得到的是测试时所用的那些版本，也不会有任何东西装进你自己的 Python。

若从检出的源码使用，请运行 `uv sync --extra ui`，并在下面的每条命令前加上 `uv run`。

## 启动

```bash
maeyomi web
```

这会启动一个本地页面并在浏览器中打开它。程序能做的一切都在页面里，所以从这里往下的内容都不是必读的。页面用一句话说明它的用途：

> 为 Barcode Battler 对战机和条形码游戏制作能玩的卡片，用你选择的语言打印出来。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/one-card-dark.png">
  <img alt="卡片制作器，左侧是设计好的角色，右侧绘出可打印的卡片" src="assets/screenshots/one-card-light.png">
</picture>

用滑块设计一个角色，拖动时卡片会随之重绘，然后把它打印出来。下方的面板会说明机器读回的数值是否与你要求的完全一致，并显示它算出的条形码。

页面最上方的 **机器或游戏** 用于选择卡片的用途：Barcode Battler II、第一代 Barcode Battler、Double、Datach Dragon Ball Z、Datach Ultraman Club、Datach SD Gundam Wars、Datach Yu Yu Hakusho、Datach J.League、Barcode World、Barcode Battler Senki、Lupin III、Donald Duck、Spider-Man、Alice no Paint Adventure、Doraemon 2、Doraemon 3、Nobita to Yousei no Kuni、J.League Excite Stage '94 或 '95、Dragon Slayer II、Hatayama Hatch 或 Datach Battle Rush。每个标签页都随之变化：卡片制作器只显示该设备读取的字段，并让滑块停在该设备的上限处；随机卡片页和超市按该设备的方式读取每个条形码；**官方原版卡片** 只列出该设备的卡组，只有一个卡组时隐藏卡组选择器；**作弊卡** 显示该设备最强的卡片。同一个条形码在不同设备上是不同的卡片。选择另一个设备会清空所有标签页并回到卡片制作器，其卡片会随着数值变化而重绘。这个选择保存在地址中，例如 `?device=dbz`，因此链接或刷新会打开同一个设备，后退按钮会回到上一个；`/` 会跳到列表上方的筛选框，按 Enter 选择第一个匹配项。在命令行中，`--device` 对 `generate`、`decode`、`cheat`、`random`、`products`、`kinds`、`abilities` 和 `official` 起同样的作用。

**你已经拥有的任何条形码也是一张卡片。** 把买来的商品上的数字输入 **读取条形码**，页面就会显示设备会把它读成什么。这一个是一瓶 Coca-Cola，机器把它读成防御值为 2400 的护甲。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/read-a-barcode-dark.png">
  <img alt="把一瓶 Coca-Cola 的条形码输入进去，读回来是一张防御值为 2400 的护甲卡片" src="assets/screenshots/read-a-barcode-light.png">
</picture>

**超市** 收录了 2958 种真实的日本食品，这样不用去购物也能玩。可以搜索，也可以按 **给我个惊喜**，把得到的九张打印出来。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/supermarket-dark.png">
  <img alt="超市标签页，列出真实的日本食品，以及设备从每个条形码读出的数值" src="assets/screenshots/supermarket-light.png">
</picture>

其余三个标签页分别打印一页随机卡片、Epoch 和 Bandai 实际发行过的 1544 张卡片，以及所选机器或游戏能读取的最强卡片。页面有英文、日文、简体中文和香港繁体中文，可用顶部的按钮切换，卡片也会以同一种语言打印。

`maeyomi web --no-open` 启动服务器但不打开浏览器，`maeyomi serve` 是同样的功能，供没有浏览器的机器使用。

## 命令行

上面的每个标签页也都是一条命令。

一页 24 张随机卡片，每张 A4 纸印九张，可由种子复现：

```bash
maeyomi random --count 24 --hp 1000-10000 --st 100-3000 --df 100-3000 \
    --seed 1234 --output cards.pdf
```

一张完全按规格制作的卡片：

```bash
maeyomi generate --name "Fire Knight" \
    --hp 5000 --attack 1800 --defense 1200 \
    --race human --class warrior --ability 17 \
    --output fire-knight.pdf
```

它会把你要求的和实际生成的并排打印出来，因此有差异的卡片不会被忽略：

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

按设备的读法读取一个条形码：

```bash
maeyomi decode 0401207237501
```

设备携带的是数字编号的能力代码，而不是具名的元素。列出它们：

```bash
maeyomi abilities
```

道具的制作方式相同。武器只带攻击，护甲只带防御，辅助道具只带一样东西：体力、药草或魔法点数。药草和魔法点数是 0 到 99 的普通计数：

```bash
maeyomi generate --name "Herb Pouch" --race support_item --herbs 99 \
    --output herbs.pdf
```

每个属性选项都接受一个精确值、一个范围或一个界限：`5000`、`5000-6000`、`>=1500`、`<=3000`。加上 `--images png` 可在 PDF 旁边导出页面图像。

当请求无法被精确满足时，`generate` 会说明是哪个字段阻碍了它，并且不写出任何内容。加上 `--nearest` 则会得到可以达到的最接近的卡片：

```bash
maeyomi generate --hp 20900 --st 11000 --df 10000 \
    --race mechanical --nearest --output golem.pdf
```

```
closest card differs by 100 across the requested stats
  df: requested 10000, produced 9900
```

距离是 HP、ST 和 DF 在显示单位下差值的总和，只计算请求中限定了的属性。种族、类别、职业、能力和速度从不近似：请求人类时，给一只鸟并不算更好地满足了请求，所以因其中某一项受阻的请求会以未满足的结果返回。

加上 `--back-read` 可以得到设备从背面而不是正面读取的卡片。这类卡片的上限更低，HP 为 49900 而非 99900，并且有四位数字共同决定属性和能力，因此可以达到的组合要少得多。

## 检查本机

`maeyomi doctor` 检查这台电脑能否打印出设备可以读取的卡片，并打印出每项检查看到的内容。它读取一个答案已知的条形码，绘制一个符号并从 PDF 中解码回来，确认日文字体已解析，按对比度和色盲阈值重新测量调色板，统计两份卡片清单，并报告运行它的环境、终端能否显示日文以及剩余空间。只有在确实出错时它才以非零状态退出。无论用哪种方式安装，都请先运行它：否则字体未能解析的问题只会以打印卡片上的空白文字的形式出现。

## 设备实际存储的内容

数据来自 [barcodebattler.net](https://barcodebattler.net/)，由解码器复现，而不是直接写进代码。

| 属性 | 正面读取 | 背面读取 |
|---|---|---|
| HP | 0 至 99900 | 0 至 49900 |
| ST | 0 至 19900 | 0 至 11900 |
| DF | 0 至 19900 | 0 至 9900 |
| 特殊能力 | 00 至 99 | 00 至 29 |

种族 0 到 4 是角色：机械、动物、水生、鸟类、人类。种族 5 到 9 是道具。职业数字 0 到 6 是战士，7 到 9 是魔法师。数值以 100 为单位存储，因此每个属性都是 100 的倍数。

有两个约束限制了可以请求的内容。触及其中任一约束的请求会被拒绝并给出原因，绝不会被悄悄修改：

- 体力高于 19900 的角色需要已公开的正面读取标记，该标记强制第三位数字为 9。这类卡片的 HP 总是以 900 结尾，速度总是 5。
- 种族 0、1 和 2 在 HP 超过 20000 时，力量和防御会被改写，因此在这个量级上并非每一对数值都能达到。其中一些代码会让设备以比显示值更高的攻击或防御作战，最高可达 24600；卡片也会印出这个数值。

## 工作原理

```
requested attributes -> digit placement -> barcode -> decoder -> compare -> accept
```

正面读取把固定的数字片段映射到各项属性上，因此反推它是放置而不是搜索：一个完全指定的请求决定了每一位数字，再计算出校验位，只留下一个候选，而暴力搜索则要遍历 10^12 个。每个候选仍然要再经过一次解码器，任何字段不一致的都会被丢弃。

背面读取不是双射。四位数字共同决定生命值、力量、防御和能力，而种族位于校验位的位置，所以它无法被放置，只能通过调整一个自由数字来凑出。可以达到的集合小到可以直接全部枚举：10000 种数字组合产生 5000 个不同的属性三元组，因为生命值的百位数字被减半了。

条形码以明确的模块宽度绘制为矢量图形，默认值为 EAN 标称值 0.33 mm。为适应版面而缩放的栅格化条形码，其模块会被不均匀地取整，从而无法扫描，而针对数字字符串的任何测试都发现不了这一点。

## 打印

请按 100% 比例打印。关闭 "适合页面"、"缩小以适合" 以及任何其他缩放选项。缩放过的页面看起来仍然正确，却会读不出来，因为扫描器测量的正是模块宽度。

卡片竖向打印，采用扑克牌尺寸 63.5 乘 88.9 mm，每张 A4 纸印九张。卡套和切纸刀正是为这个尺寸设计的。这是本项目自己的选择：Epoch 从未公布过其卡片的尺寸，也没有任何收藏者页面、拍卖列表或维基记录过它。尺寸位于 [`layout.py`](src/maeyomi/rendering/layout.py) 中的 `CARD_WIDTH_MM` 和 `CARD_HEIGHT_MM`，修改这两个数字，其他一切都会随之变化，因为网格、间距、裁切标记和适配检查都是由它们推导出来的。

每页都遵循印刷厂的要求：

| 项目 | 数值 | 原因 |
|---|---|---|
| 出血 | 单页 1.5 mm，使用 `--print-shop` 时为 3 mm | 即使裁切稍有偏差，切口处仍然有墨 |
| 卡片间距 | 4 mm，是出血的两倍 | 每张卡片沿自己的线裁切，不与相邻卡片共用一条线 |
| 安全区 | 距裁切线 4 mm | 读者需要的内容不会落在可能被裁掉的位置 |
| 裁切标记 | 从出血边缘开始的角标 | 印刷厂据此裁切，且没有任何线条穿过卡片 |
| 模块宽度 | 0.330 mm | GS1 EAN-13 标称值 |
| 条高 | 22.85 mm | GS1 标称值，也是手动刷卡容差的全部 |

`--print-shop` 会以同一批卡片的另一种形式输出：每页一张卡片，页面尺寸为卡片加 3 mm 出血，没有标尺也没有标记，这正是商业印刷厂自己的说明所要求的。

每页底部有一把 100 mm 的标尺，以厘米标注刻度，卡片上方还有一行英文和日文说明，写明每个条形码应有的宽度。第一次打印后，用尺子比一下。如果偏短，说明打印机缩放了页面；请修正打印对话框的设置后重新打印。这两条区域都位于卡片网格之外，会随边角料一起裁掉。

## 读取手头的条形码

`maeyomi decode 4901085061169` 会打印出设备会把任何条形码读成什么，加上 `-o card.pdf --name "Tomato sauce"` 还会同时打印卡片。网页上的 **读取条形码** 提供同样的功能：输入印在条下方的数字，它会显示卡片的种类、三个数值、特殊能力，以及设备是从正面还是背面读取它，并附上一张可以打印的卡片。

`maeyomi kinds` 以两种语言列出设备所知的每一种卡片，以及每种卡片的作用。


当年这台机器就是这样玩的。任何商品条形码都是一张卡片，所以一瓶番茄酱是一名角色，一袋薯片是一件武器。日本商品代码和其他代码一样可用：`4902102072618` 是一瓶茶，读出来是防御值为 2400 的护甲。

## 超市

`maeyomi products --search 茶` 列出匹配的真实日本食品，`--count 9 --seed 3` 随机取出几样，`-o shopping.pdf` 则把它们打印出来。网页上的 **超市** 提供同样的功能，还有一个 **给我个惊喜** 按钮。番茄酱对面条是一场公平的较量。


这个货架是 [Open Food Facts](https://world.openfoodfacts.org/) 的一个精选子集，只保留分配给日本公司的条形码，即 45 和 49 前缀，并且带有解码器接受的日文名称。他们的数据以 Open Database License 发布，本子集沿用相同条款，并在 **来源** 一节中注明出处。卡片上的任何内容都不来自他们：每个数字都是本项目的解码器从条形码中读出的，所以名称错了只会让笑话失色，别无影响。

`maeyomi decode <barcode>` 在网页上还会向 Open Food Facts 查询条形码对应的名称，知道时就填上。这只是一项便利功能：查询失败不会让卡片有任何改变。

## 真实卡片

`maeyomi official --list` 列出 Epoch 和 Bandai 发行的 40 份卡片清单、每份有多少张卡片可以打印，以及每份清单是为哪台设备编写的；`maeyomi official --set candy -o candy.pdf` 打印其中一份，省略 `--set` 则打印全部 1544 张。网页上的 **官方原版卡片** 提供同样的功能。

Epoch 从未发布过机器可读的清单，因此条形码来自收藏者录入自己所持卡片的页面，位于 [wikiwiki.jp](https://wikiwiki.jp/barcode/)。每个条目都保留了其页面的地址。有五个条目未通过自身的校验位，这意味着有人打错了一位数字；错的是哪一位无法确定，因此它们被列出并排除，而不是靠猜测修复。每张卡片上印的数字是由本项目的解码器从条形码读出的，而不是从维基复制的。

有六份清单是为第一代 Barcode Battler 编写的：初始卡组、The Demon Army God Mars Appears、Chuhai Khan Strikes Back、The Final Battle: God versus Mother、糖果卡，以及 CoroCoro Comic 的 Obocchama-kun 卡片，后者注明可用于 Barcode Battler，而不是 II。其中四份用第一代设备的表描述标志；God Mars 清单没有印任何数字，其中也没有魔法师，没有药草或魔法道具，这些只有 II 才能读取。正伝3 和 正伝4 清单需要 Barcode Battler II Double 的 7 读法，正伝4 的卡片有一半用到它。其余 24 份按 II 的读法打印。

Zelda、Shogaku Ninensei 杂志和 Street Fighter II 的卡片来自 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的 `deeta.js` 中的卡片清单，它以英文发布这些清单，因此这些卡片使用英文名称。Zelda 的一件道具，即红色药水，同时也是 II 桌游中的一张卡片。

Dragon Slayer、Doraemon: Nobita's Dinosaur、Obocchama-kun 和 Meiji 的卡片在任何地方都没有录入，因此它们的条形码是从 [barcodebattler.co.uk 发布的卡片扫描图](https://www.barcodebattler.co.uk/scans/Japan/)中逐张读出的，并根据卡片正面印的数字与名称对应起来。Meiji 卡片中只有编号 1 和 5 的被扫描过。

Super Mario World 卡组，以及 Irwin 在美国和加拿大、Tomy 在英国和欧洲销售的卡包，来自 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的卡片页面，这些页面录入了每一个条形码。Tomy 的卡片是 Epoch 的代码配上当地名称，名称不同的每个版本各有一份清单：英国、爱尔兰和意大利共用一份，德国、西班牙和法国各自为部分道具改了名。Irwin 的美国版和加拿大版卡片名称和代码相同，加拿大版在英文旁附有法文，因此它们算作一份清单。Irwin 修改了全部十张道具卡和新闻卡的代码：其中九张读出的仍是同一道具，而它的 Life Crystals 正面印的是 "EP = ??" 而不是数字，读出为 300，而 Epoch 的这张卡片印的和读出的都是 1600。

Datach Dragon Ball Z 附带 40 张卡片。它的[说明书](https://setsumei.cloudfree.jp/famicom/datachdragonballz/datachdragonballz.html)称，其中一些卡片没有条形码，包括 Super Saiyan Goku、Super Saiyan Trunks、final-form Frieza 和 Perfect Cell，并请玩家在这些卡片上贴一个自己的条形码。带条形码的 35 张，加上一张特别的 Super Saiyan Goku 卡片，就是这里打印的 36 张，取自 [puNES](https://github.com/punesemu/puNES) 模拟器源代码中的清单，每张在加入前都经过 MAME 中的游戏读取。

只有当条形码的条以及空都至少有三种不同宽度时，该游戏才会读取它；它在程序中 $B085 处把测得的宽度分类，宽度种类更少的扫描会被拒绝。三种宽度为 1、2 和 4 的代码只在某些刷卡速度下能读取。本程序为该游戏构造的每个代码在任何速度下都能读取，`maeyomi decode --device dbz` 会指出游戏拒绝的代码，超市也会标出它无法读取的商品。

Datach Ultraman Club 附带 40 张卡片，其中两张是空白的。其余 38 张是 [retrostuff.org](https://retrostuff.org/2019/03/23/bandai-datach-ultraman-club-spokon-fight-barcodes-for-mame/) 从一套盒装产品中读出的代码，按 puNES 清单的命名方式命名，并且每张都经过 MAME 中的游戏读取。后来的 Datach 游戏不会像 Dragon Ball Z 那样拒绝代码：它们能读取条只有两种宽度的代码。它们的共同问题在于条或空恰好是 1、2 和 4 个模块宽的代码，这类代码只在某些刷卡速度下能读取；已发行的 Ultraman Club 卡片中有五张属于这种代码。本程序为 Datach 游戏构造的每张卡片都避开了它们。

SD Gundam Wars 附带 40 张卡片。其中 37 张带有两个条形码，底边是机动战士，顶边是指令，一张特别卡片各带一个：共 76 个条形码，由 [retrostuff.org](https://retrostuff.org/2019/05/12/bandai-datach-sd-gundam-gundam-wars-barcodes-for-mame/) 从一套盒装产品中读出，与 puNES 清单一致，并且每个都经过 MAME 中的游戏读取。

Yu Yu Hakusho 附带 40 张卡片，其中三张没有条形码。其余 37 张来自 [archive.org](https://archive.org/details/yu-yu-hakusho-bakuto-ankoku-bujutsue-box-front) 在一整套卡片的扫描图旁保存的电子表格，按该表格的命名方式命名，并且每张都经过 MAME 中的游戏读取。

J.League Super Top Players 附带 40 张卡片，每张带四个条形码：一家俱乐部加三名球员，或四名球员。这 160 个条形码来自 [archive.org](https://archive.org/details/j-league-super-top-players-manual) 在一整套卡片的扫描图旁保存的电子表格，按游戏自身的球员名录命名，并且每个都经过 MAME 中的游戏读取。

Barcode World 附带 24 张卡片和一张白色空白卡。它们的条形码是从 [barcodebattler.co.uk 发布的卡片扫描图](https://www.barcodebattler.co.uk/scans/Japan/BarcodeWorld/)中读出的，按卡片上印的名称命名，并且每张都经过 MAME 中的游戏读取。它的武器、护具和道具是在战斗中扫描的，而不是在角色画面扫描，因此它们按其本来的类型打印，不带数字。

根据[它的日文维基百科条目](https://ja.wikipedia.org/wiki/%E3%83%90%E3%83%BC%E3%82%B3%E3%83%BC%E3%83%89%E3%83%90%E3%83%88%E3%83%A9%E3%83%BC%E6%88%A6%E8%A8%98_%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E6%88%A6%E5%A3%AB%E5%87%BA%E6%92%83%E3%81%9B%E3%82%88!)，Barcode Battler Senki 附带 10 张卡片：5 张角色卡、3 张道具卡和 2 张白色空白卡。没有人公开过它们的条形码，因此 `maeyomi official --device senki` 会说明这一点，而不是打印一张空白页。Lupin III、Donald Duck、Spider-Man 和 Alice no Paint Adventure 完全没有附带卡片，三款 Doraemon 游戏也没有。

Epoch 为 Excite Stage '94 给 1994 年 J.League 的 12 家俱乐部各印制了一张名单卡。它们的条形码是从 [barcodebattler.co.uk 发布的扫描图](https://www.barcodebattler.co.uk/scans/Japan/J-League/)中读出的，Excite Stage '94 和 '95 都会把每一张读成道具卡，已在 MAME 中核对。

## 秘籍

`maeyomi cheat -o cheat.pdf`，或网页上的 **作弊卡** 标签页；在页面任意位置输入上、上、下、下、左、右、左、右、B、A 也能打开它。这张卡片是一名机械魔法师，体力 99900，攻击翻倍。设备显示攻击 14600、防御 19900，作战时攻击为 24600。

其中没有任何硬编码的内容。生成器让满体力的每个正面读取角色都经过解码器自身的运算，保留作战时攻击与防御合计最高的那一个，并避开所有尚未确定的分支。隐藏的 24600 是设备自身的行为：体力高于 20000 且攻击数字为 46 的机械角色会获得一项显示中从不出现的加成。根据 [barcodebattler.net](https://barcodebattler.net/page21.htm)，曾有人看到一台设备用代码 4994699095453 恰好表现出这一点。卡片把这个隐藏值印在其特殊能力旁边。

`maeyomi cheat --items -o cheat.pdf` 会加上五件道具，每件都达到其数字所能容纳的最大值：攻击 9900 的武器、防御 9900 的护甲、体力 99900 的药水、99 个药草和 99 点魔法点数。每件道具都会把一种不同的、有文献记载的能力赋予使用者：对手防御降低 80%，自身防御提高一半，对手体力减半，对手攻击减半，以及对手的特殊能力被取消。多件道具的能力是否叠加没有文献记载，因此这些都不依赖于叠加。

该命令会说明每件道具可由哪些职业使用，依据是 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)中的装备表。魔法师不能持有武器或护甲，所以刀刃和盾牌适用于任何职业的战士，而药水、药草和水晶都可以配合秘籍魔法师使用。

`maeyomi cheat --device bb1 --items -o cheat.pdf` 为第一代 Barcode Battler 做同样的事：一名每项数值都达到上限的战士，体力 19900、攻击 9900、防御 9900，且攻击翻倍，外加达到上限的武器、护甲和药水。这名战士的职业为 9，该设备允许这一职业装备所有武器，并让类型 0 到 4 的武器再多获得一半的攻击。

`maeyomi cheat --device double --items -o cheat.pdf` 是三者中最强的：一张攻击 99900、防御 99900 的 Double 卡片，这是该资料所述的上限，再加上让对手体力减半的能力。这个能力取自体力的两位数字，因此体力剩下 92900。道具使用 II 的道具，每件都带有 Double 自己的表中的一种能力。Double 的装备表从未公开，因此该命令不会说明哪个职业可以使用哪件道具。

`maeyomi cheat --device dbz --items -o cheat.pdf` 是必杀技等级 3 的 Super Saiyan Goku，HP 99500、BP 48250、DP 33250。HP 是游戏规则所能容纳的最大值；BP 和 DP 是条形码仍能构成十位十进制数字的最强组合，是通过搜索所有可打印卡片找到的。这比游戏隐藏在自身程序中的那张卡片强十倍以上。道具是每种最强效果各一件：senzu bean、Shenron、Kami、Guru、ultra divine water，以及等级 4 的 Porunga。

`maeyomi cheat --device ultraman -o cheat.pdf` 是 PW、ST 和 SP 全部为 9900 的 Ultraman，这是游戏的两张表相加所能达到的最大值。

`maeyomi cheat --device sdgundam -o cheat.pdf` 是 Quin Mantha，这台机动战士的 HP、AP 和 DP 合计最高，所有加成都处于最高值：HP 7700、AP 7000、DP 9000、CP 6。

`maeyomi cheat --device yuyu -o cheat.pdf` 是游戏隐藏的角色 SP Toguro，HP 9999、SP 9999，并拥有他的全部四个招式。游戏只有在收到一串精确的比特时才会给出它，Bandai 印制的卡片中没有任何一张带有这串比特。

`maeyomi cheat --device barcodeworld -o cheat.pdf` 是一名职业 9 的魔法师，HP 49900、ST 19900、DF 19900、魔法 10、药草 5，每个数值都达到游戏所能读取的最大值。`maeyomi cheat --device senki -o cheat.pdf` 是为 Barcode Battler Senki 准备的同一名魔法师。

四款密码画面游戏各得到其最有用的效果：Lupin III 中是无伤，Donald Duck 中是带有所有能力和 12 颗心的天空关卡，Spider-Man 中是无限生命，Alice no Paint Adventure 中是所有后期标志都已设置的故事最后一幕。Spider-Man 把其中三种效果保存在不同的位置，因此无限生命、双倍体力和首领体力减半可以依次扫描，三种效果都会保留。

Doraemon 2 得到 99 条命，Doraemon 3 从世界 5 开始，Nobita to Yousei no Kuni 让 Doraemon 无敌。

J.League Excite Stage '95 得到整体实力提升 253，这是任何卡片所能提升的最大值。

Dragon Slayer II 开局时所有状态都处于最高值。

Hatayama Hatch 得到一名巫师，体力 99900，攻击和防御 19900，魔法 99。

Datach Battle Rush 打印一对卡片，对应的机器人攻击、防御和速度为 233，这是它们能同时达到的最大值，恢复为 255。游戏的求和中有一个字节会溢出回绕，因此最大的部件并不能造出最强的机器人。

J.League Excite Stage '94 得到 Gamamoto Kunikuni，这名隐藏球员各项评级均为 A。

## 语言与图示

从网页打印的卡片使用页面的语言：英文、日文、简体中文或香港繁体中文。在命令行中，放在命令之前的 `--language` 起同样的作用，取值为 `en`、`ja`、`zh-Hans` 或 `zh-Hant-HK`，例如 `maeyomi --language ja cheat -o cheat.pdf`；省略它则把英文和日文并排打印。生物的种类、它的战斗方式、三项战斗数值、特殊能力以及刷卡说明都随之变化。每项信息还配有图示，供还不识字的孩子使用：一条带有象形图标的彩色色带表示生物种类，心形、剑和盾表示数值，特殊能力则有一个象形图标，显示它改变什么以及朝哪个方向改变，例如一把带向上箭头的剑表示 "自身攻击翻倍"。传达含义的是箭头的方向，而不是颜色。

特殊能力的文字采用两种语言的公开措辞：日文照抄自 barcodebattler.net/page05.htm，英文是本项目对同一页面的解读。种族、类别和属性的名称是本项目自己的翻译，使用小读者最先学会的平假名和片假名。两种中文也都是本项目自己的翻译；角色、机体、球员和游戏的名称保持英文版所印的样子，因为这些游戏大多从未有过可以借用名称的中文版。有一项测试会在每台设备上渲染每张官方卡片、每张作弊卡、每款游戏列出的每个条目以及分布广泛的 2000 个条形码，只要其中印出的任何一个词没有中文就会失败。玩家选择的名字按输入原样打印，任何文字均可。

网页用顶部的按钮在英文、日文、简体中文和香港繁体中文之间切换，会记住所选语言，并以浏览器的语言启动。

日文和中文使用的是每个 PDF 阅读器都自带的字体，但只是引用而非嵌入。若要交给印刷厂，请发送页面图像而不是 PDF，使用 `--images png`，这些图像为 600 dpi，文字已经绘制在内。

## 不用鼠标或视力也能使用

页面仅用键盘即可操作。跳转链接可以越过页头，六个标签页只占一个 Tab 停靠点，用方向键在它们之间移动，Home 和 End 跳到两端，每个控件都会绘制可见的焦点框，每个控件至少 44 乘 44 像素，食品列表可以用键盘滚动。语言切换会更改文档的 `lang`，因此屏幕阅读器会随之切换发音。当系统要求减少动画时，动画会被取消。

axe-core 在全部六个标签页上，无论浅色还是深色配色，针对 WCAG 2.2 A 和 AA 以及它自己的最佳实践规则集，都没有报告任何违规。规则集无法完成的检查是在真实浏览器中手动完成的：焦点框是从获得焦点的元素上读回的，而不是从样式表中读取的。

PDF 在没有结构树的情况下尽可能携带信息。每个 PDF 都有自己的名称，因此阅读器会朗读 "Barcode Battler II card: Tea" 而不是 `sheet.pdf`，并且 PDF 会告诉阅读器优先使用这个标题而不是文件名。文档声明了其语言、作者以及内容。卡片上的每个字都是真实文本：名称、数字、特殊能力、每一种语言，以及条下方的数字，所有这些都能按人阅读的顺序从文件中取出：先是种类，然后是名称，接着每个数值排在说明其含义的标签之后，然后是能力，最后是条形码。

缺少的内容：ReportLab 不输出标签树，因此这些文件不是 PDF/UA 文件。没有标题、没有列表，象形图标也没有替代文本，英日双语并排打印的 PDF 声明为英文，其中的日文段落也没有逐一标记为日文。象形图标重复的是旁边文字已经说明的内容，因此它们没有描述不会造成信息损失。验证工具会把这些文件判定为未加标签。

## 颜色

卡片会交给商业印刷厂，这往往意味着按黑白印刷；卡片还会交到孩子手中，大约十二个男孩中就有一个分辨不出红色和绿色。这两种情况都通过测量来处理。

没有任何东西仅靠颜色区分。每条色带都有自己的名称和象形图标，每个战斗数值都有自己的形状和两个字母的标签，因此以灰度打印的卡片仍能表达彩色时所表达的全部内容。

`src/maeyomi/rendering/colour.py` 包含相关运算，`tests/rendering/test_palette.py` 用它来约束调色板：

| 检查项 | 阈值 | 依据 |
|---|---|---|
| 色带上的白色文字，彩色和灰度下 | 4.5 比 1 | WCAG 2.2，最低对比度 |
| 象形图标与其底块，彩色和灰度下 | 3 比 1 | WCAG 2.2，非文本对比度 |
| 两条角色色带，在正常视觉以及红色盲、绿色盲和蓝色盲下 | 20 个 CIE 1976 单位 | 两种颜色被看作不同颜色而不是同一颜色的两种深浅时的距离 |
| 以灰度打印的两条角色色带 | 1.15 比 1 | 可见的色调差 |
| 武器或护甲的一次性版本与永久版本，灰度下 | 1.5 比 1 | 它们共用一个象形图标，因此色调要承担更多区分作用 |

二色视觉模拟采用 Brettel、Vienot 和 Mollon 的线性近似。还会把一页栅格化、转换为灰度，并解码其中的每个条形码，确保打印结果在完全没有彩色的打印机上也能用。

## 来源

解码器移植自采用 MIT 许可证的 [Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator) 中的 `src/BarcodeRead.as`。属性范围、读取类型规则和能力表来自 [barcodebattler.net](https://barcodebattler.net/)。卡片测试数据来自 [wikiwiki.jp](https://wikiwiki.jp/barcode/) 上的卡片清单，每个条目都记录了来源页面和抓取日期。每个来源、从中取用的内容以及所用的许可证如下：

- **[Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator)**，作者 finalfighter，MIT。`src/maeyomi/decoder/` 中的解码器移植了它的 `src/BarcodeRead.as`，测试语料 `tests/fixtures/simulator_corpus.json` 来自它的卡片清单。
- **[barcodebattler.net](https://barcodebattler.net/)**，即 yuko2ch.net 的镜像，以及作者在设备上测试过打印代码的 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)：属性范围、读取类型规则、能力表、高体力加成、职业 6 的判定以及 Double 的 7 读法。仅取用事实。
- **[wikiwiki.jp](https://wikiwiki.jp/barcode/)**：日文卡片清单，每个条目都保留了页面和地址。
- **[barcodebattler.co.uk](https://www.barcodebattler.co.uk/)**：其 `deeta.js` 中的 Zelda、Shogaku Ninensei 和 Street Fighter II 清单；其卡片页面上的 Super Mario World、Irwin 和 Tomy 清单；Barcode Battler II 技术说明；以及读取 Dragon Slayer、Doraemon、Obocchama-kun、Meiji、Barcode World 和 J.League 俱乐部条形码所用的卡片扫描图。仅取用事实；本项目中没有出现它的任何代码。
- **[puNES](https://github.com/punesemu/puNES)**，GPL-2：36 张 Datach Dragon Ball Z 卡片的条形码和名称，每张都由游戏本身核对过。本项目中没有出现来自 puNES 的任何代码。
- **[retrostuff.org](https://retrostuff.org/)** 和 **[archive.org](https://archive.org/)**：Ultraman Club、SD Gundam Wars、Yu Yu Hakusho 和 J.League Super Top Players 的条形码。
- **[一个 5ch 帖子](https://mevius.5ch.net/test/read.cgi/toy/1226667612/)**，第 484 楼：Double 的 7 读法中的种族。
- **[MAME](https://www.mamedev.org/)** 0.289 在检查中运行每一款游戏。游戏规则来自每款游戏自身的程序；不附带任何 ROM 字节，每个 ROM 都以其校验和记录在 `artifacts.manifest.json` 中。
- **[Open Food Facts](https://world.openfoodfacts.org/)**，Open Database License 1.0：`src/maeyomi/products/japan.json` 中的条形码、产品名称和品牌，这一子集仍遵循[同一许可证](https://opendatacommons.org/licenses/odbl/1-0/)。在线查询在其 user agent 中注明本项目，这是他们的条款所要求的。
- **VITIMan/barcode-battler-engine**，GPL-3，未被使用：没有任何代码、结构或命名来自它。它只是指向了本项目直接抓取的 wikiwiki.jp 清单。

各来源存在分歧之处，相关问题记录在 `src/maeyomi/decoder/uncertainties.py` 中，包括每个来源的说法以及所作的选择。解码器遵循模拟器，除非在设备上测试过打印代码的来源另有说法：高体力加成遵循 [barcodebattler.net](https://barcodebattler.net/page21.htm) 和一份 [note.com 分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)，职业 6 为战士。已记录的问题中有五个会把未经验证的数值印到卡片上，生成器拒绝输出任何会触及它们的代码。
