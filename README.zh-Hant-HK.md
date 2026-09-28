<div align="center">

# maeyomi

<strong>為 Barcode Battler 機器和條碼遊戲列印可以玩的卡片。</strong>

[English](README.md) &nbsp;|&nbsp; [日本語](README.ja.md) &nbsp;|&nbsp; [简体中文](README.zh-Hans.md) &nbsp;|&nbsp; 香港繁體中文

[![ci](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml/badge.svg)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.14-blue)](pyproject.toml)

<p align="center">
  <a href="#安裝">安裝</a> &nbsp;|&nbsp;
  <a href="#開啟">開啟</a> &nbsp;|&nbsp;
  <a href="#使用命令行">命令行</a> &nbsp;|&nbsp;
  <a href="#運作原理">運作原理</a> &nbsp;|&nbsp;
  <a href="#超級市場">超級市場</a> &nbsp;|&nbsp;
  <a href="#資料來源">資料來源</a>
</p>

</div>

已轉錄 **1544** 張官方卡片。**2958** 件日本食品。**100** 種特殊能力。卡片可用英文、日文或中文列印。測試覆蓋率 **100%**。Barcode Battler II 卡片已在真機上驗證。

---

Barcode Battler II 讀取條碼後，單憑數字就得出一個角色或一件道具。Maeyomi 是這部機器自己對正面讀取的叫法，也就是產生角色的那種讀法。這個程式把這套運算倒過來：要求一張防禦 2400 的護甲卡，它就會算出機器會這樣讀取的條碼，然後列印出來。

每個條碼在印上紙之前都會再解碼一次，每一頁列印出來的頁面都會點陣化，再用條碼閱讀器讀回。列印好的卡片已在一部實體 Barcode Battler II 上掃過。

1991 年的第一代 Barcode Battler 以自己的方式讀取同樣的數字：每個角色都是戰士，體力上限是 19900，攻擊和防禦上限是 9900，而兩位數的代碼是另一張表裏的旗標，所以 18 在這裏是主角，在 II 則是攻擊加倍。在 `decode`、`generate` 和 `cheat` 加上 `--device bb1`，就可以為它製作卡片。它的解碼器能重現為它編寫的四份清單中已公開的 113 張卡片，而至今還沒有任何為它製作的卡片在實體第一代 Barcode Battler 上讀取過，為它印出的每一張卡紙都註明了這一點。

Barcode Battler II Double，即 1993 年的 II²，沒有讀取器，要從一部 II 接收代碼。它按 II 的方式讀取，只有以 7 開頭而第十位是 8 的代碼例外，這種代碼它用自己的方式讀取：攻擊和防禦可達 99900，特殊能力則是體力其中兩位數字。`--device double` 為它製作卡片，依據是 [barcodebattler.net](https://barcodebattler.net/bb2c0.html) 上的「BBIIダブルC0」。這種讀法解釋了正伝3 清單中任何 II 讀法都解釋不了的十一張卡片。它的種族是攻擊的百位數減 5，這是一份[收藏家的報告](https://mevius.5ch.net/test/read.cgi/toy/1226667612/)在正伝3 和正伝4 的敵方卡片上發現的；十一張全部吻合，而百位數低於 5 時，種族未知。它的速度仍然未知。Double 還命名了兩個 II 沒有的職業，分別是職業 4 的祭司和職業 6 的聖戰士，並有自己的一張特殊能力表。

Bandai 的 Datach Dragon Ball Z: Gekitou Tenkaichi Budoukai 是 1992 年的 Famicom 遊戲，附有一部條碼閱讀器。`--device dbz` 為它製作卡片。遊戲把十位數字的各個位元打散成一個 40 位元的數，再從中讀出一個角色或一件道具、一個必殺技等級，以及 HP、BP 和 DP。這條規則是從遊戲自己的程式中讀出來的，而在遊戲於 MAME 中接受的全部 232 個代碼上，解碼器都與在 MAME 中運行的遊戲一致。用 `--character` 選擇角色或道具，可用遊戲顯示的名稱或 id；用 `--level` 選擇等級，用 `--hp`、`--bp` 和 `--dp` 設定數值；如果那些確切數值無法列印，加上 `--nearest` 就會取最接近而可以列印的卡片。數值夠高的角色會變成更強的形態，與遊戲一樣。至今還沒有任何為它製作的卡片在實體 Datach 上讀取過，為它印出的每一張卡紙都註明了這一點。

Datach Ultraman Club: Supokon Fight! 是 Bandai 的第二款 Datach 遊戲，1993 年推出，它把條碼讀成 51 種類型之一，0 至 27 是超人英雄和怪獸，32 起是道具，另外再讀出三個它稱為 PW、ST 和 SP 的數值，每個由 0 至 9900，以 100 為一級。`--device ultraman` 為它製作卡片：用 `--character` 選擇類型，可用遊戲顯示的名稱或編號，再按順序用 `--hp`、`--st` 和 `--df` 設定三個數值。這個範圍內的每個值都可以列印。規則是從遊戲的程式中讀出來的，並與在 MAME 中運行的遊戲本身一致，涵蓋它的 38 張已發行卡片，以及每種類型各一、共 51 個自行構造的代碼。至今還沒有任何為它製作的卡片在實體 Datach 上讀取過。

Datach SD Gundam: Gundam Wars 同樣在 1993 年推出，把條碼讀成 63 部機動戰士之一或 59 張指令卡之一。機動戰士從自己的 HP、AP、DP 和 CP 出發，各自加上一張表中的加成，並攜帶兩種近距離武器之一和兩種遠距離武器之一；指令卡則帶有它的效果和所需的 CP。`--device sdgundam` 為它製作卡片：用 `--character` 選擇卡片，可用名稱、型號或編號；用 `--hp`、`--st` 和 `--df` 設定數值，分別是 HP、AP 和 DP；用 `--pick sr=1`、`--pick lr=5` 或 `--pick cp=11` 設定武器和 CP。介乎遊戲能容納的兩個數值之間的數字會變成最接近的一個，命令會說明這一點。規則在 MAME 中與遊戲一致，涵蓋它的 76 個已發行條碼，以及每個欄位各一、共 122 個自行構造的代碼。至今還沒有任何為它製作的卡片在實體 Datach 上讀取過。

Datach Yu Yu Hakusho: Bakutou Ankoku Bujutsukai 同樣是 1993 年的遊戲，把條碼讀成 22 名角色或 10 件道具之一，另外還有一名遊戲隱藏的角色。角色的 HP 和 SP 是它自己固定的，任何條碼都改變不了；條碼決定的是它能使用四招中的哪幾招。道具按四個等級之一增加 HP 或 SP，或者改變對戰模式的一條規則。`--device yuyu` 為它製作卡片：用 `--character` 選擇卡片，用 `--pick moves=15` 選擇招式，每招一個位元，再用 `--pick level=3` 設定道具的等級。規則在 MAME 中與遊戲一致，涵蓋它的 37 張已發行卡片，以及遍及每個角色、招式組合和道具、共 183 個自行構造的代碼。至今還沒有任何為它製作的卡片在實體 Datach 上讀取過。

Datach J.League Super Top Players 是 1994 年的遊戲，把條碼讀成 1993 年 J.League 十支球會的 150 名球員之一，或者其中一支球會。卡片指定一名真實球員，本身不帶任何數值，所以遊戲保留每名球員的能力，也就沒有給它的秘技卡片。`--device jleague` 為它製作卡片：用 `--character` 選擇球員或球會，可用名稱或編號。規則在 MAME 中與遊戲一致，涵蓋它的 160 個已發行條碼，以及為觸及遊戲容許的每個摺疊值而構造的 12 個代碼。至今還沒有任何為它製作的卡片在實體 Datach 上讀取過。

Datach 遊戲 Crayon Shin-chan: Ora to Poi Poi 的程式中完全沒有讀取條碼的部分，所以不能接受卡片。

Datach Battle Rush: Build Up Robot Tournament 在它的 Robo Factory 用依次掃描的兩張卡片組裝一部機械人，`--device battlerush` 製作這一對卡片。第一張帶有機械人的編號、頭部、身體、肩膀、腳部和駕駛員；第二張帶有武器和四個等級。遊戲故意拒絕商店的條碼：它自己卡片的最後一位，比 EAN 應有的校驗位小一或二，所以這些卡片以那一位數字列印，普通條碼閱讀器不會接受。用 `--character` 以編號或 16 名對手之一的名稱選擇機械人，再用 `--pick head=3 --pick attack=7` 等選擇零件和等級。規則是從遊戲的程式中讀出來的，在試過的每一對卡片上都與 MAME 中的遊戲一致；MAME 只部分模擬遊戲的存檔晶片，所以檢查時要寫入它的兩個位元組才能進入工廠。目前不知道有任何 Bandai 所印卡片的清單。

Sunsoft 的 Barcode World 是 1992 年的 Famicom 遊戲，透過一部連接 Famicom 的 Barcode Battler II 讀取卡片，所以能讀取任何條碼。`--device barcodeworld` 為它製作卡片。遊戲讀取數字的方式與 Barcode Battler II 大致相同，以百為單位：HP 最高 49900，ST 和 DF 最高 19900，其中體力超過 19900 需要百位是 9 而且速度是 5，魔法和藥草則由職業決定。用 `--character` 選擇戰士或魔法師，用 `--hp`、`--st` 和 `--df` 設定數值，用 `--pick job=3`、`--pick speed=8` 和 `--pick ability=45` 設定職業、速度和能力。規則在 MAME 中與遊戲一致，涵蓋 211 個代碼，其中包括它的 24 張已發行卡片，也涵蓋在這裏構造並試過的每一張卡片。

Epoch 的 Barcode Battler Senki 是 1993 年的 Super Famicom 遊戲，透過接在 Barcode Battler II Interface 上的 Barcode Battler II 讀取卡片，`--device senki` 為它製作卡片。它讀取數字的方式與 Barcode World 相同，只有三點不同。8 位數的代碼到達時前面會多出五個零，因為介面把 Barcode Battler II 的空位轉成零。從末端讀取的道具，會把力量的個位保持在十以下。而印在 Interface 盒子上的代碼，在兩種對戰模式中都會打開聲音測試，而不是產生卡片。規則在 MAME 中與遊戲一致，涵蓋 253 個代碼，其中包括在這裏構造並試過的每一張卡片。劇情模式中一間隱藏商店 Black Store 會用較小的偏移量讀取從末端讀取的卡片，所以這類卡片也會顯示該商店給它的 HP、ST 和 DF；這種讀法在 MAME 中與遊戲的 232 個代碼一致，測試時是直接設定商店地圖事件所設的旗標，而不是走到商店。MAME 0.289 把每一位數字送到 Super Famicom 時都錯開了一個位元，所以檢查時透過一個專門為此編寫的介面把代碼送入遊戲。

另外四款 Epoch 的 Super Famicom 遊戲透過同一個介面在密碼屏幕讀取代碼，每個代碼觸發一份固定清單中的一個效果，而不是產生角色：Lupin III: Densetsu no Hihou o Oe! 用 `--device lupin`，Donald Duck no Mahou no Boushi 用 `--device donald`，Spider-Man: Lethal Foes 用 `--device spiderman`，Alice no Paint Adventure 用 `--device alice`。效果包括無傷、無限生命或道具全滿等秘技，跳到某一關、某一章或某個結局，以及聲音測試。`maeyomi kinds --device lupin` 列出一款遊戲的效果，`--character` 按名稱或編號選擇其中一個。每條規則都是從遊戲的程式中讀出來的，並在試過的每個代碼上與 MAME 中的遊戲一致：Lupin III 250 個，Donald Duck 247 個，Spider-Man 221 個，Alice 253 個。不符合任何規則的代碼會被讀取，但不會有任何作用。

三款 Super Famicom 的 Doraemon 遊戲以同樣方式讀取代碼，每款各有兩個屏幕：Doraemon 2 用 `--device doraemon2`，在密碼屏幕和關卡的道具選單；Doraemon 3 用 `--device doraemon3`，在密碼屏幕和遊玩時的裝備選單；Nobita to Yousei no Kuni 用 `--device yousei`，在密碼屏幕和城鎮地圖的道具屏幕。密碼屏幕提供無敵、99 條命或較後的世界等秘技，選單則提供秘密道具、武器、護具和物品。每張卡片都註明要在哪個屏幕掃描。Doraemon 4 帶有同樣的讀取程式碼，卻從不呼叫它，所以遊戲中沒有任何屏幕接受條碼。

J.League Excite Stage '94 在季前賽之前，於名單屏幕的 Barcode Battler 面板讀取代碼，`--device excite94` 為它製作卡片。校驗位是 4 或以上的代碼是 240 名隱藏球員之一，每名都有名字，以及踢球、射門、跑動和盤球的評級，守門員則是防守的評級；校驗位較低的是道具卡，與 Excite Stage '95 的相似。用 `--character` 選擇球員或道具，用 `--pick value=253` 設定道具的數量。名字和評級直接取自遊戲自己的數據表，除了一名沒有任何代碼的數字能觸及的球員外，每名球員都可以列印。PK 模式以同樣方式讀取球員，而道具卡則以自己的方式讀取，讀成六種 PK 道具類型之一和 0 至 9 的等級，卡片上也會顯示；各種 PK 類型在比賽中有甚麼作用，尚未追查。兩條規則都在試過的每個代碼上與 MAME 中的遊戲一致，其中 168 個在 PK 模式。

Super Famicom 的 J.League Excite Stage '95 在公開賽、聯賽、錦標賽或夢幻賽之前，於 Barcode Battler II 輸入屏幕讀取代碼，`--device excite95` 為它製作卡片。每個代碼都是道具卡：整體實力、盤球、傳球速度、射球速度或守門員的撲救，提升 0 至 253，或者是最多 4 點讓分的特殊卡，或令犯規不出牌的特殊卡。用 `--character` 選擇道具，用 `--pick value=253` 設定數量。規則在試過的每個代碼上都與 MAME 中的遊戲一致。PK 模式以另一種方式讀取代碼，沒有建模。

Falcom 的 Dragon Slayer: Eiyuu Densetsu II 由 Epoch 在 1993 年推出 Super Famicom 版，會在標題選單和野外選單讀取代碼，`--device dslayer2` 為它製作卡片。標題選單提供各種秘技，例如所有狀態升到最高、經驗值和金錢加倍、怪物清單或聲音模式。在野外，以 038438816 開頭的代碼會給予編號為其最後三位數字的道具，999 開啟所有傳送點，另有幾個代碼可在沒有持有的情況下使用燈、Bisna 果實、休息蘑菇或地圖。Epoch 為 Barcode Battler II 印製的 Dragon Slayer 卡片，遊戲並不會特別處理。

Hatayama Hatch no Paro Yakyuu News! Jitsumei Ban 是 Epoch 1993 年的棒球遊戲，會在它的 Battle Baseball Board 上把代碼讀成一名 battler，`--device hatayama` 為它製作卡片。按 Epoch 卡片格式排列的代碼會原樣讀取：耐力最高 99900，攻擊和防禦以百為單位最高 19900，巫師的魔法最高 99；其他代碼則從最後幾位數字推算。用 `--character` 選擇戰士或巫師，用 `--hp`、`--st` 和 `--df` 設定數值，用 `--pick mp=99` 設定魔法。同一代碼的最後一位數字，也會在遊戲另外兩個條碼屏幕上選擇一種戰術和一個圖像，每張卡片都會印出是哪一個。遊戲附有 14 支球隊的卡片，但沒有人公開過它們的條碼。

## 支援的機器和遊戲

下面每一部機器和每一款遊戲，在命令行都是一個 `--device`，在網頁上都是 **機器或遊戲** 下的一個選項。機器、遊戲和它們卡包的照片可在
[barcodebattler.co.uk](https://www.barcodebattler.co.uk/scans/Japan/) 找到。

| 機器或遊戲 | 日文名稱 | 運行平台 | `--device` |
|---|---|---|---|
| Barcode Battler | バーコードバトラー | 獨立機器 | `bb1` |
| Barcode Battler 2 | バーコードバトラー2 | 獨立機器 | `bb2` |
| Barcode Battler 2 Double | バーコードバトラー2 ダブル | 獨立機器 | `double` |
| Alice no Paint Adventure | アリスのペイントアドベンチャー | Super Famicom，經 Barcode Battler II 讀取 | `alice` |
| Barcode Battler Senki | バーコードバトラー戦記 | Super Famicom，經 Barcode Battler II 讀取 | `senki` |
| Donald Duck no Mahou no Boushi | ドナルドダックの魔法のぼうし | Super Famicom，經 Barcode Battler II 讀取 | `donald` |
| Doraemon 2 | ドラえもん2 のび太のトイズランド大冒険 | Super Famicom，經 Barcode Battler II 讀取 | `doraemon2` |
| Doraemon 3 | ドラえもん3 のび太と時の宝玉 | Super Famicom，經 Barcode Battler II 讀取 | `doraemon3` |
| Doraemon: Yousei no Kuni | ドラえもん のび太と妖精の国 | Super Famicom，經 Barcode Battler II 讀取 | `yousei` |
| Dragon Slayer II | ドラゴンスレイヤー英雄伝説II | Super Famicom，經 Barcode Battler II 讀取 | `dslayer2` |
| Hatayama Hatch | はた山ハッチのパロ野球ニュース!実名版 | Super Famicom，經 Barcode Battler II 讀取 | `hatayama` |
| J.League Excite Stage '94 | J.リーグエキサイトステージ'94 | Super Famicom，經 Barcode Battler II 讀取 | `excite94` |
| J.League Excite Stage '95 | J.リーグエキサイトステージ'95 | Super Famicom，經 Barcode Battler II 讀取 | `excite95` |
| Lupin III | ルパン三世 伝説の秘宝を追え! | Super Famicom，經 Barcode Battler II 讀取 | `lupin` |
| Spider-Man: Lethal Foes | スパイダーマン リーサルフォーズ | Super Famicom，經 Barcode Battler II 讀取 | `spiderman` |
| Datach Battle Rush | データック バトルラッシュ | Famicom Datach | `battlerush` |
| Datach Dragon Ball Z | データック ドラゴンボールZ | Famicom Datach | `dbz` |
| Datach J.League | データック Jリーグ スーパートッププレイヤーズ | Famicom Datach | `jleague` |
| Datach SD Gundam Wars | データック SDガンダム ガンダムウォーズ | Famicom Datach | `sdgundam` |
| Datach Ultraman Club | データック ウルトラマン倶楽部 | Famicom Datach | `ultraman` |
| Datach Yu Yu Hakusho | データック 幽遊白書 | Famicom Datach | `yuyu` |
| Barcode World | バーコードワールド | Famicom，經 Barcode Battler II 讀取 | `barcodeworld` |

## 安裝

```bash
brew tap gufranco/maeyomi https://github.com/gufranco/maeyomi
brew install gufranco/maeyomi/maeyomi
```

這個 tap 就是本儲存庫。由於儲存庫不叫 `homebrew-maeyomi`，Homebrew 需要明確的 URL；這樣 formula、原始碼和發行版本就放在一起，而不是放在另一個會逐漸走樣的儲存庫。

安裝時會一併裝上 Python 3.14，並從已提交的 lockfile 建立一個獨立環境，所以你得到的是測試時所用的版本，你自己的 Python 也不會多出任何東西。

如果從 checkout 使用，先執行 `uv sync --extra ui`，再在下面每條命令前加上 `uv run`。

## 開啟

```bash
maeyomi web
```

這會啟動一個本機頁面，並用瀏覽器打開它。程式能做的一切都在那裏，所以此後的內容不必細讀。頁面用一句話說明它的用途：

> 為 Barcode Battler 機和條碼遊戲製作可以玩的卡，用你選擇的語言列印出來。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/one-card-dark.png">
  <img alt="卡片製作器，左邊是設計好的角色，右邊是繪製出來、可以列印的卡片" src="assets/screenshots/one-card-light.png">
</picture>

用滑桿設計角色，移動時卡片會跟著重繪，然後列印。下面的面板會說明機器讀回的數值是否與你要求的完全相同，並顯示它算出的條碼。

**機器或遊戲** 位於頁面最前，決定卡片給哪部機器或哪款遊戲使用：Barcode Battler II、第一代 Barcode Battler、Double、Datach Dragon Ball Z、Datach Ultraman Club、Datach SD Gundam Wars、Datach Yu Yu Hakusho、Datach J.League、Barcode World、Barcode Battler Senki、Lupin III、Donald Duck、Spider-Man、Alice no Paint Adventure、Doraemon 2、Doraemon 3、Nobita to Yousei no Kuni、J.League Excite Stage '94 或 '95、Dragon Slayer II、Hatayama Hatch 或 Datach Battle Rush。每個分頁都跟隨這個選擇：卡片製作器只顯示該裝置讀取的欄位，滑桿停在該裝置的上限；隨機卡紙和超級市場按該裝置的方式讀取每個條碼；**真正的卡** 只列出該裝置的卡組，只有一組時就隱藏卡組選擇器；**作弊卡** 顯示該裝置最強的卡片。同一個條碼在每部裝置上都是不同的卡片。選擇另一部裝置會清空所有分頁，並回到卡片製作器，而卡片會隨數值變化重繪。這個選擇會保存在網址中，例如 `?device=dbz`，所以連結或重新載入都會打開同一部裝置，返回按鈕則回到上一部；`/` 跳到清單上方的篩選框，按 Enter 選取第一個符合項目。在命令行上，`--device` 對 `generate`、`decode`、`cheat`、`random`、`products`、`kinds`、`abilities` 和 `official` 有同樣作用。

**你已經擁有的任何條碼也是一張卡片。** 把買回來的商品上的數字輸入 **讀取條碼**，頁面就會顯示裝置怎樣理解它。這個例子是一瓶 Coca-Cola，機器把它讀成防禦 2400 的護甲。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/read-a-barcode-dark.png">
  <img alt="把一瓶 Coca-Cola 的條碼輸入後，讀回成一張防禦 2400 的護甲卡" src="assets/screenshots/read-a-barcode-light.png">
</picture>

**超級市場** 收錄了 2958 件真實的日本食品，不用去購物也能玩。可以搜尋，或按 **給我驚喜**，然後列印得到的九件。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/supermarket-dark.png">
  <img alt="超級市場分頁，列出真實的日本食品，以及裝置從每個條碼讀出的數值" src="assets/screenshots/supermarket-light.png">
</picture>

其餘三個分頁分別列印一整張隨機卡片、Epoch 和 Bandai 實際發行的 1544 張卡片，以及所選機器或遊戲會讀取的最強卡片。頁面有英文、日文、簡體中文和香港中文，用頂部的按鈕切換，卡片也以同一種語言列印。

`maeyomi web --no-open` 啟動伺服器但不開瀏覽器，而 `maeyomi serve` 功能相同，供沒有瀏覽器的電腦使用。

## 使用命令行

上面每個分頁也都是一條命令。

一張 24 張隨機卡片的卡紙，每頁 A4 放九張，可由種子重現：

```bash
maeyomi random --count 24 --hp 1000-10000 --st 100-3000 --df 100-3000 \
    --seed 1234 --output cards.pdf
```

一張按確切規格製作的卡片：

```bash
maeyomi generate --name "Fire Knight" \
    --hp 5000 --attack 1800 --defense 1200 \
    --race human --class warrior --ability 17 \
    --output fire-knight.pdf
```

它會把你要求的值和實際產生的值並排顯示，所以有差異的卡片不會不知不覺溜過：

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

按裝置的方式讀取條碼：

```bash
maeyomi decode 0401207237501
```

裝置使用的是數字能力代碼，而不是有名稱的屬性。列出它們：

```bash
maeyomi abilities
```

道具也以同樣方式製作。武器只帶攻擊，護甲只帶防禦，輔助道具只帶一樣東西，即體力、藥草或魔法點數。藥草和魔法點數是 0 至 99 的純粹數量：

```bash
maeyomi generate --name "Herb Pouch" --race support_item --herbs 99 \
    --output herbs.pdf
```

每個數值選項都接受一個確切值、一個範圍或一個界限：`5000`、`5000-6000`、`>=1500`、`<=3000`。加上 `--images png` 可在 PDF 旁邊匯出頁面圖像。

當要求無法完全滿足時，`generate` 會說明是哪個欄位阻礙了它，而且不會寫出任何檔案。加上 `--nearest` 就會改為取得最接近而可達到的卡片：

```bash
maeyomi generate --hp 20900 --st 11000 --df 10000 \
    --race mechanical --nearest --output golem.pdf
```

```
closest card differs by 100 across the requested stats
  df: requested 10000, produced 9900
```

距離是 HP、ST 和 DF 以顯示單位計算的差距總和，只計算要求中有限制的數值。種族、類別、職業、能力和速度永遠不會近似：要求人類時，給一隻鳥並不算更好，所以卡在這些欄位上的要求會以未滿足的結果返回。

加上 `--back-read` 可製作裝置從背面而非正面讀取的卡片。這類卡片的上限較低，HP 是 49900 而非 99900，而且有四位數字同時影響數值和能力，所以能達到的組合少得多。

## 檢查電腦

`maeyomi doctor` 檢查這部電腦能否列印裝置會讀取的卡片，並顯示每項檢查看到的結果。它會讀取一個答案已知的條碼，繪製一個符號並從 PDF 中解碼出來，確認日文字型已成功解析，按對比度和色盲門檻重新量度配色，點算兩份卡片清單，並報告運行它的環境、終端機能否顯示日文，以及還剩多少空間。只有在真的出錯時，它才會以非零值結束。無論用哪種方式安裝，都先執行它：字型沒有解析成功的話，要到印出的卡片上文字變成空白才會發現。

## 裝置實際儲存的數值

資料來自 [barcodebattler.net](https://barcodebattler.net/)，由解碼器重現，而不是寫死在解碼器中。

| 屬性 | 正面讀取 | 背面讀取 |
|---|---|---|
| HP | 0 至 99900 | 0 至 49900 |
| ST | 0 至 19900 | 0 至 11900 |
| DF | 0 至 19900 | 0 至 9900 |
| 特殊能力 | 00 至 99 | 00 至 29 |

種族 0 至 4 是角色，依次為機械、動物、水棲、鳥類、人類。種族 5 至 9 是道具。職業數字 0 至 6 是戰士，7 至 9 是魔法師。數值以 100 為單位儲存，所以每項數值都是 100 的倍數。

有兩項限制會收窄可以要求的範圍。碰到其中任何一項的要求都會被拒絕並附上原因，絕不會被悄悄修改：

- 體力超過 19900 的角色需要已公開的正面讀取標記，這會迫使第三位數字為 9。這種卡片的 HP 必定以 900 結尾，速度必定是 5。
- 種族 0、1 和 2 在體力超過 20000 時，力量和防禦會被改寫，所以在這個級別並非每一對數值都能達到。其中一些代碼會令裝置以比顯示更高的攻擊或防禦作戰，最高 24600；卡片也會印出這個數值。

## 運作原理

```
requested attributes -> digit placement -> barcode -> decoder -> compare -> accept
```

正面讀取把固定的數字片段對應到各項屬性，所以把它倒過來是擺放而不是搜尋：完全指定的要求會決定每一位數字，再計算出校驗位，最後只剩一個候選，而不是暴力搜尋要走遍的 10^12 個。每個候選仍然會送回解碼器，任何欄位不一致的都會被捨棄。

背面讀取不是雙射。四位數字同時影響體力、力量、防禦和能力，而種族位於校驗位的位置，所以不能直接擺放，只能靠調整一位自由數字來湊出來。可達到的集合小得可以全部列舉：10000 種數字組合產生 5000 組不同的數值三元組，因為體力的百位數會減半。

條碼以明確的模組寬度繪製成向量，預設為 EAN 標稱的 0.33 mm。點陣化的條碼若被縮放以配合版面，模組會被不均勻地捨入而無法掃描，這是任何針對數字字串的測試都捕捉不到的。

## 列印

按 100% 比例列印。關閉「符合頁面大小」、「縮小以符合」及任何其他縮放。縮放過的頁面看起來仍然正確，卻會無法讀取，因為掃描器量度的正是模組寬度。

卡片直向列印，撲克尺寸 63.5 乘 88.9 mm，每張 A4 放九張。這是卡套和切紙機所針對的尺寸。這是本項目自己的選擇：Epoch 從未公布自家卡片的尺寸，任何收藏家網頁、拍賣刊登或 wiki 都沒有記錄。尺寸存放在
[`layout.py`](src/maeyomi/rendering/layout.py) 的 `CARD_WIDTH_MM` 和 `CARD_HEIGHT_MM`，改變這兩個數字就會移動其他一切，因為網格、間距、標記和尺寸檢查全都由它們推導出來。

每張卡紙都遵循印刷店的要求：

| 項目 | 數值 | 原因 |
|---|---|---|
| 出血 | 卡紙上 1.5 mm，用 `--print-shop` 時 3 mm | 裁切稍有偏差，仍然切在有墨的地方 |
| 卡片之間的間距 | 4 mm，是出血的兩倍 | 每張卡片沿自己的線裁切，不與旁邊的卡片共用一條線 |
| 安全區 | 距裁切線 4 mm | 讀者需要的內容不會放在可能被裁掉的位置 |
| 裁切標記 | 從出血邊緣開始的角位短線 | 印刷商按此裁切，沒有線穿過卡片 |
| 模組寬度 | 0.330 mm | GS1 EAN-13 標稱值 |
| 條高 | 22.85 mm | GS1 標稱值，也是手動掃過時的全部容差 |

`--print-shop` 寫出同樣卡片的另一種形式：每頁一張卡片，頁面尺寸為卡片加 3 mm 出血，沒有尺規也沒有標記，這正是商業印刷商自己的指引所要求的。

每張卡紙底部都有一把 100 mm 的尺，以厘米標數，卡片上方還有一行英文和日文，說明每個條碼應量得的寬度。第一次列印後拿尺對一對。如果量出來較短，就是打印機縮放了頁面；更正對話框的設定再印一次。兩條帶都位於卡片網格之外，所以會隨裁下的廢料一併去掉。

## 讀取手上已有的條碼

`maeyomi decode 4901085061169` 會顯示裝置對任何條碼的理解，加上 `-o card.pdf --name "Tomato sauce"` 則會同時列印卡片。網頁的 **讀取條碼** 有同樣功能：輸入條碼下方印著的數字，它就會顯示卡片種類、三個數值、特殊能力，以及裝置從正面還是背面讀取，並附上可以列印的卡片。

`maeyomi kinds` 以兩種語言列出裝置認識的每一種卡片，以及每種的作用。


當年這部機器正是這樣玩的。任何商品條碼都是一張卡片，所以一瓶茄汁是一名角色，一包薯片是一件武器。日本的商品代碼和其他代碼一樣可用：`4902102072618` 是一瓶茶，是防禦 2400 的護甲。

## 超級市場

`maeyomi products --search 茶` 列出符合的真實日本食品，`--count 9 --seed 3` 隨機抽取一些，`-o shopping.pdf` 把它們列印出來。網頁的 **超級市場** 有同樣功能，還有一個 **給我驚喜** 按鈕。茄汁對麵條，是一場公平的對決。


這個貨架是 [Open Food Facts](https://world.openfoodfacts.org/) 的精選子集，只保留發給日本公司的條碼，即 45 和 49 字頭，並且要有解碼器接受的日文名稱。他們的數據以 Open Database License 發布，這個子集沿用相同條款，並在 **資料來源** 中註明出處。卡片上沒有任何東西來自他們：每個數字都由本項目的解碼器從條碼讀出，所以名稱錯了只會破壞一個笑話，別無影響。

網頁上的 `maeyomi decode <barcode>` 也會向 Open Food Facts 查詢條碼的名稱，知道的話就填上。這只是一項便利功能：查詢失敗不會改變卡片的任何內容。

## 真正的卡片

`maeyomi official --list` 列出 Epoch 和 Bandai 發行的 40 份卡片清單、每份有多少張可以列印，以及每份清單為哪部裝置而寫；`maeyomi official --set candy -o candy.pdf` 列印其中一份，不加 `--set` 則列印全部 1544 張。網頁的 **真正的卡** 有同樣功能。

Epoch 從未公開機器可讀的清單，所以條碼來自收藏家把自己所藏卡片逐張輸入的頁面，位於
[wikiwiki.jp](https://wikiwiki.jp/barcode/)。每個項目都保留其頁面的網址。有五個項目未能通過自身的校驗位，表示有人打錯了一位數字；錯的那一位無法確定，所以它們會被列出並剔除，而不是靠猜測修補。每張卡片上印的數字都由本項目的解碼器從條碼讀出，不是從 wiki 抄來的。

六份清單是為第一代 Barcode Battler 而寫的：原版卡組、The Demon Army God Mars Appears、Chuhai Khan Strikes Back、The Final Battle: God versus Mother、糖果卡，以及 CoroCoro Comic 的 Obocchama-kun 卡片，後者註明可配合 Barcode Battler 而非 II 使用。其中四份用第一代裝置的表描述旗標；God Mars 清單沒有印任何數值，也沒有魔法師和藥草或魔法道具，這些只有 II 會讀取。正伝3 和正伝4 清單需要 Barcode Battler II Double 的 7 讀取，正伝4 有一半卡片用到它。其餘 24 份按 II 的方式列印。

Zelda、Shogaku Ninensei 雜誌和 Street Fighter II 的卡片取自 [barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的
`deeta.js` 中的卡片清單，該檔案以英文發布，所以這些卡片帶有英文名稱。其中一件 Zelda 道具，即紅色藥水，也是 II 棋盤遊戲的一張卡片。

Dragon Slayer、Doraemon: Nobita's Dinosaur、Obocchama-kun 和 Meiji 的卡片在任何地方都沒有轉錄，所以它們的條碼是從
[barcodebattler.co.uk 發布的卡片掃描圖](https://www.barcodebattler.co.uk/scans/Japan/)中逐張讀出的，並以卡片正面印著的數字把每張與其名稱對應起來。Meiji 卡片只有編號 1 和 5 的被掃描過。

Super Mario World 卡組，以及 Irwin 在美國和加拿大、Tomy 在英國和歐洲出售的卡包，取自
[barcodebattler.co.uk](https://www.barcodebattler.co.uk/) 的卡片頁面，那裏把每個條碼都打了出來。Tomy 的卡片是 Epoch 的代碼配上當地名稱，名稱有差異的每個版本各一份清單：英國、愛爾蘭和意大利共用一份，德國、西班牙和法國則各自改了一些道具的名稱。Irwin 的美國和加拿大卡片名稱和代碼相同，加拿大版在英文旁附有法文，所以算作一份清單。Irwin 改了全部十張道具和新聞卡片的代碼：九張讀出來仍是同一道具，而它的 Life Crystals 正面印著「EP = ??」而不是數字，讀出來是 300，Epoch 的卡片則印著並讀出 1600。

Datach Dragon Ball Z 附有 40 張卡片。它的
[說明書](https://setsumei.cloudfree.jp/famicom/datachdragonballz/datachdragonballz.html)
指出其中一些沒有條碼，包括超級撒亞人孫悟空、超級撒亞人杜拉格斯、最終形態菲利和完全體沙魯，並請玩家自行在這些卡片上貼一個。帶有條碼的 35 張，加上一張特別的超級撒亞人孫悟空卡，就是這裏列印的 36 張，取自
[puNES](https://github.com/punesemu/puNES) 模擬器原始碼中的清單，每張在加入之前都經過 MAME 中的遊戲讀取。

遊戲只有在條碼的條和空位都至少有三種不同寬度時才會讀取；它在程式中位於 $B085 的地方把量得的寬度分類，少於三類的掃描會被拒絕。寬度為 1、2 和 4 的代碼只在某些掃描速度下才能讀取。這個程式為遊戲構造的每個代碼在任何速度下都能讀取，`maeyomi decode --device dbz` 會指出遊戲拒絕的代碼，超級市場也會標示它讀不到的商品。

Datach Ultraman Club 附有 40 張卡片，其中兩張是空白的。另外 38 張是 [retrostuff.org](https://retrostuff.org/2019/03/23/bandai-datach-ultraman-club-spokon-fight-barcodes-for-mame/)
從一盒套裝中讀出的代碼，按 puNES 清單的名稱命名，每張都經過 MAME 中的遊戲讀取。後期的 Datach 遊戲不會像 Dragon Ball Z 那樣拒絕代碼：條只有兩種寬度的代碼它們也會讀取。它們共同的問題在於條或空位剛好是 1、2 和 4 個模組寬的代碼，這種代碼只在某些掃描速度下才能讀取；已發行的 Ultraman Club 卡片中有五張是這種代碼。這個程式為 Datach 遊戲構造的每張卡片都避開了它們。

SD Gundam Wars 附有 40 張卡片。其中 37 張帶有兩個條碼，底邊是機動戰士，頂邊是指令，另有一張特別卡片兩種各帶一個：共 76 個條碼，由 [retrostuff.org](https://retrostuff.org/2019/05/12/bandai-datach-sd-gundam-gundam-wars-barcodes-for-mame/)
從一盒套裝中讀出，與 puNES 清單一致，每個都經過 MAME 中的遊戲讀取。

Yu Yu Hakusho 附有 40 張卡片，其中三張沒有條碼。其餘 37 張取自 [archive.org](https://archive.org/details/yu-yu-hakusho-bakuto-ankoku-bujutsue-box-front)
在一整套卡片掃描圖旁保存的試算表，按該試算表的名稱命名，每張都經過 MAME 中的遊戲讀取。

J.League Super Top Players 附有 40 張卡片，每張帶有四個條碼，分別是一支球會和三名球員，或四名球員。這 160 個條碼取自 [archive.org](https://archive.org/details/j-league-super-top-players-manual)
在一整套卡片掃描圖旁保存的試算表，按遊戲自己的球員名冊命名，每個都經過 MAME 中的遊戲讀取。

Barcode World 附有 24 張卡片和一張白色空白卡。它們的條碼是從
[barcodebattler.co.uk 發布的卡片掃描圖](https://www.barcodebattler.co.uk/scans/Japan/BarcodeWorld/)中讀出的，按卡片上印的名稱命名，每張都經過 MAME 中的遊戲讀取。它的武器、護具和道具在戰鬥中掃描，而不是在角色屏幕，所以印出來只標明是甚麼，沒有數值。

根據
[它的日文維基百科條目](https://ja.wikipedia.org/wiki/%E3%83%90%E3%83%BC%E3%82%B3%E3%83%BC%E3%83%89%E3%83%90%E3%83%88%E3%83%A9%E3%83%BC%E6%88%A6%E8%A8%98_%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E6%88%A6%E5%A3%AB%E5%87%BA%E6%92%83%E3%81%9B%E3%82%88!)，
Barcode Battler Senki 附有 10 張卡片：5 張角色、3 張道具和 2 張白色空白卡。沒有人公開過它們的條碼，所以 `maeyomi official --device senki` 會說明這一點，而不是列印一張空白卡紙。Lupin III、Donald Duck、Spider-Man 和 Alice no Paint Adventure 完全沒有附卡片，三款 Doraemon 遊戲也沒有。

Epoch 為 Excite Stage '94 印製了 1994 年 12 支 J.League 球會各一張的名單卡。它們的條碼是從
[barcodebattler.co.uk 發布的掃描圖](https://www.barcodebattler.co.uk/scans/Japan/J-League/)中讀出的，Excite Stage '94 和 '95 都把每一張讀成道具卡，已在 MAME 中核實。

## 秘技

`maeyomi cheat -o cheat.pdf`，或網頁的 **作弊卡** 分頁；在頁面任何地方輸入上、上、下、下、左、右、左、右、B、A 也會打開它。這張卡片是一名機械種族的魔法師，體力 99900，攻擊加倍。裝置顯示 14600 攻擊和 19900 防禦，而作戰時用 24600 攻擊。

沒有任何部分是寫死的。產生器把每個滿體力的正面讀取角色都經解碼器自身的運算走一遍，保留作戰時攻擊和防禦加起來最高的一個，並避開所有未解決的分支。隱藏的 24600 來自裝置本身：體力超過 20000、攻擊數字為 46 的機械角色，會獲得一個顯示上從不出現的加成。根據
[barcodebattler.net](https://barcodebattler.net/page21.htm)，曾有人看到一部裝置用代碼 4994699095453 正是這樣表現。卡片把這個隱藏數值印在特殊能力旁邊。

`maeyomi cheat --items -o cheat.pdf` 加入五件道具，每件都達到其數字所能容納的最大值：攻擊 9900 的武器、防禦 9900 的護甲、體力 99900 的藥水、99 份藥草和 99 點魔法點數。每件都會把一種不同的、有記載的能力傳給使用者：對手防禦減少 80%、你自己的防禦提升一半、對手體力減半、對手攻擊減半，以及取消對手的特殊能力。多件道具的能力會否疊加並無記載，所以這些都不依賴這一點。

命令會說明每件道具可由哪些職業使用，依據是
[note.com 的分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)中的裝備表。魔法師不能持有武器或護甲，所以刀和盾是給任何職業的戰士用的，而藥水、藥草和水晶都可以配合秘技魔法師使用。

`maeyomi cheat --device bb1 --items -o cheat.pdf` 為第一代 Barcode Battler 做同樣的事：一名每項數值都達上限的戰士，體力 19900、攻擊 9900、防禦 9900，攻擊加倍，另加達上限的武器、護甲和藥水。這名戰士是職業 9，該裝置讓這個職業可裝備所有武器，並令類型 0 至 4 的武器攻擊再增加一半。

`maeyomi cheat --device double --items -o cheat.pdf` 是三者中最強的：一張攻擊 99900、防禦 99900 的 Double 卡，這是該來源所述的上限，並帶有令對手體力減半的能力。這個能力是體力其中兩位數字，所以體力剩下 92900。道具是 II 的道具，各自帶有 Double 自己的表中的一種能力。Double 沒有已公開的裝備表，所以命令不會說明哪個職業可以使用哪件道具。

`maeyomi cheat --device dbz --items -o cheat.pdf` 是必殺技等級 3 的超級撒亞人孫悟空，HP 99500、BP 48250、DP 33250。HP 是遊戲規則能容納的最大值；BP 和 DP 是條碼仍能成為十位十進制數字的最強組合，透過搜尋每張可列印的卡片找出。這比遊戲在自己程式中隱藏的卡片強十倍以上。道具是每種最強效果各一：仙豆、神龍、天神、大長老、超神水，以及等級 4 的波倫加。

`maeyomi cheat --device ultraman -o cheat.pdf` 是 PW、ST 和 SP 全部為 9900 的 Ultraman，這是遊戲兩張表加起來所能達到的最大值。

`maeyomi cheat --device sdgundam -o cheat.pdf` 是 Quin Mantha，即 HP、AP 和 DP 合計最高的機動戰士，每項加成都在最高：HP 7700、AP 7000、DP 9000，CP 6。

`maeyomi cheat --device yuyu -o cheat.pdf` 是遊戲隱藏的角色 SP Toguro，擁有 9999 HP、9999 SP 和他全部四招。遊戲只會為一串確切的位元給出這個角色，而 Bandai 印製的卡片沒有一張帶有它。

`maeyomi cheat --device barcodeworld -o cheat.pdf` 是職業 9 的魔法師，HP 49900、ST 19900、DF 19900、10 點魔法和 5 份藥草，每個數值都是遊戲會讀取的最大值。`maeyomi cheat --device senki -o cheat.pdf` 是給 Barcode Battler Senki 的同一名魔法師。

四款密碼屏幕遊戲各得到最有用的效果：Lupin III 的無傷，Donald Duck 擁有所有能力和 12 顆心的天空關卡，Spider-Man 的無限生命，以及 Alice no Paint Adventure 中所有後期旗標都已設定的故事最後一幕。Spider-Man 把其中三個效果存放在不同位置，所以無限生命、雙倍體力和頭目體力減半可以接連掃描，三者都會保留。

Doraemon 2 得到 99 條命，Doraemon 3 從世界 5 開始，Nobita to Yousei no Kuni 則令 Doraemon 無敵。

J.League Excite Stage '95 得到整體實力提升 253，這是任何卡片能提升的最大值。

Dragon Slayer II 開始時所有狀態都在最高。

Hatayama Hatch 得到一名巫師，耐力 99900，攻擊和防禦 19900，魔法 99。

Datach Battle Rush 列印一對卡片，對應攻擊、防禦和速度都是 233 的機械人，這是三者能同時達到的最大值，回復則是 255。遊戲的總和中有一個位元組會溢位，所以最大的零件並不會造出最強的機械人。

J.League Excite Stage '94 得到 Gamamoto Kunikuni，這名隱藏球員每項都評為 A。

## 語言和圖像

從網頁列印的卡片使用頁面的語言：英文、日文、簡體中文或香港中文。在命令行上，把 `--language` 放在命令之前，配合 `en`、`ja`、`zh-Hans` 或 `zh-Hant-HK` 也有同樣作用，例如 `maeyomi --language ja cheat -o cheat.pdf`；不加的話，就會以英文和日文並排列印。生物的種類、作戰方式、三個戰鬥數值、特殊能力和掃描說明，全都跟隨這個語言。每項資訊也配有圖像，給還不會讀任何一種文字的小朋友：一條彩色帶配上表示生物種類的圖示，心形、劍和盾代表數值，還有一個表示特殊能力的圖示，顯示它改變甚麼以及往哪個方向改變，例如一把配有向上箭嘴的劍代表「自己的攻擊加倍」。意思由箭嘴的方向表達，從不依靠它的顏色。

特殊能力的文字是兩種語言中已公開的措辭：日文抄自 barcodebattler.net/page05.htm，英文是本項目對同一頁的解讀。種族、類別和數值名稱是本項目自己的翻譯，用的是小朋友最先學會的平假名和片假名。兩種中文同樣是本項目的翻譯；角色、機體、球員和遊戲的名稱保留英文版印出的樣子，因為這些遊戲大多從未推出中文版，沒有中文名稱可以沿用。有一項測試會在每部裝置上繪製每張官方卡片、每張作弊卡、每款遊戲列出的每個項目，以及分佈廣泛的 2000 個條碼，只要其中印出的任何一個詞沒有中文，測試就會失敗。玩家自選的名字會照輸入的樣子列印，任何一種文字都可以。

網頁用頂部的按鈕在英文、日文、簡體中文和香港中文之間切換，會記住選擇，並以瀏覽器的語言開始。

日文和中文使用每個 PDF 閱讀器都附有的字型排版，這些字型是引用而非嵌入。交給印刷店時，請改為傳送頁面圖像而非 PDF，即 `--images png`，這些圖像是 600 dpi，文字已經繪製好。

## 不用滑鼠或看不見時也能使用

頁面只用鍵盤就能操作。跳過連結可越過刊頭，六個分頁是一個停留點，用方向鍵在其間移動，Home 和 End 跳到兩端，每個控制項都會顯示可見的焦點框，每個控制項至少 44 乘 44 像素，食品清單也可以用鍵盤捲動。語言切換會改變文件上的 `lang`，所以屏幕閱讀器會隨之轉換語音。系統要求減少動畫時，動畫就會取消。

axe-core 在六個分頁上，無論淺色還是深色配色，按 WCAG 2.2 A 和 AA 以及它自己的最佳做法規則集檢查，都沒有報告任何違規。規則集做不到的檢查，是在真實瀏覽器中人手完成的：焦點框是從取得焦點的元素上讀回的，而不是從樣式表讀取。

PDF 帶有在沒有結構樹的情況下 PDF 所能帶有的內容。每個檔案都有自己的標題，所以閱讀器會讀出「Barcode Battler II card: Tea」而不是 `sheet.pdf`，並被告知優先使用該標題而非檔案名稱。文件聲明了它的語言、作者和性質。卡片上每個字都是真正的文字：名稱、數字、特殊能力、每一種語言，以及條碼下方的數字，全部都能按人閱讀的順序從檔案中取回：先是種類，然後是名稱，接著每個數字跟在說明它量度甚麼的標籤之後，然後是能力，最後是條碼。

欠缺的部分：ReportLab 不會輸出標籤樹，所以這些不是 PDF/UA 檔案。沒有標題、沒有清單，圖示也沒有替代文字，日文段落亦沒有逐一標記為日文。圖示只是重複旁邊文字已經說明的內容，所以沒有描述也不會缺失任何資訊。驗證工具會說這些檔案沒有標籤。

## 色彩

卡片會交給商業印刷商，這往往意味著以黑白印刷；卡片也會交到小朋友手上，而大約每十二個男孩就有一個分不清紅色和綠色。兩種情況都以量度處理。

沒有任何東西單靠顏色區分。每條色帶都有自己的名稱和圖示，每個戰鬥數值都有自己的形狀和兩個字母的標籤，所以以灰階印出的卡片仍然傳達彩色版的全部內容。

`src/maeyomi/rendering/colour.py` 負責運算，
`tests/rendering/test_palette.py` 用它檢驗配色：

| 檢查 | 門檻 | 來源 |
|---|---|---|
| 色帶上的白色文字，彩色和灰階 | 4.5 比 1 | WCAG 2.2，最低對比度 |
| 圖示相對其底塊，彩色和灰階 | 3 比 1 | WCAG 2.2，非文字對比 |
| 兩條角色色帶，在正常色覺以及紅色盲、綠色盲和藍色盲下 | 20 個 CIE 1976 單位 | 兩種顏色被看成不同顏色、而非同一顏色兩種深淺的距離 |
| 兩條角色色帶以灰階列印 | 1.15 比 1 | 可見的色調級差 |
| 武器或護甲的一次性版本和永久版本，灰階 | 1.5 比 1 | 它們共用一個圖示，所以色調要承擔更多 |

色盲模擬採用 Brettel、Vienot 和 Mollon 的線性近似。卡紙也會被點陣化、轉為灰階，再把上面每個條碼解碼，所以印出的成品經得起完全沒有彩色的打印機。

## 資料來源

解碼器移植自採用 MIT 授權的
[Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator) 中的 `src/BarcodeRead.as`。
屬性範圍、讀取類型規則和能力表來自
[barcodebattler.net](https://barcodebattler.net/)。卡片測試資料來自
[wikiwiki.jp](https://wikiwiki.jp/barcode/) 上的卡片清單，每個項目都記錄了來源頁面和擷取日期。每個來源、從中取用了甚麼，以及採用哪種授權：

- **[Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator)**，
  作者 finalfighter，MIT。`src/maeyomi/decoder/` 中的解碼器移植了它的
  `src/BarcodeRead.as`，測試語料庫 `tests/fixtures/simulator_corpus.json`
  來自它的卡片清單。
- **[barcodebattler.net](https://barcodebattler.net/)**，即 yuko2ch.net 的鏡像，以及
  [note.com 的分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)，
  其作者曾在裝置上測試列印出來的代碼：屬性範圍、讀取類型規則、能力表、高體力加成、職業 6 的判定，以及 Double 的 7 讀取。只取事實。
- **[wikiwiki.jp](https://wikiwiki.jp/barcode/)**：日本的卡片清單，每個項目都保留頁面和網址。
- **[barcodebattler.co.uk](https://www.barcodebattler.co.uk/)**：來自其 `deeta.js` 的 Zelda、Shogaku Ninensei 和 Street Fighter II 清單；來自其卡片頁面的 Super Mario World、Irwin 和 Tomy 清單；Barcode Battler II 技術筆記；以及讀出 Dragon Slayer、Doraemon、Obocchama-kun、Meiji、Barcode World 和 J.League 球會條碼所用的卡片掃描圖。只取事實；這裏沒有用到它的任何程式碼。
- **[puNES](https://github.com/punesemu/puNES)**，GPL-2：36 張 Datach Dragon Ball Z 卡片的條碼和名稱，每張都經遊戲本身核實。這裏沒有用到 puNES 的任何程式碼。
- **[retrostuff.org](https://retrostuff.org/)** 和
  **[archive.org](https://archive.org/)**：Ultraman Club、SD Gundam Wars、Yu Yu Hakusho 和 J.League Super Top Players 的條碼。
- **[一個 5ch 討論串](https://mevius.5ch.net/test/read.cgi/toy/1226667612/)**，
  第 484 帖：Double 的 7 讀取種族。
- **[MAME](https://www.mamedev.org/)** 0.289 在檢查中運行每一款遊戲。遊戲規則來自每款遊戲自己的程式；沒有附帶任何 ROM 位元組，每個 ROM 都在 `artifacts.manifest.json` 中以校驗和列明。
- **[Open Food Facts](https://world.openfoodfacts.org/)**，Open Database License
  1.0：`src/maeyomi/products/japan.json` 中的條碼、商品名稱和品牌，這個子集仍採用
  [相同授權](https://opendatacommons.org/licenses/odbl/1-0/)。線上查詢會按他們條款的要求，在 user agent 中寫明本項目的名稱。
- **VITIMan/barcode-battler-engine**，GPL-3，並未使用：沒有取用它的任何程式碼、結構或命名。它只是指向了這裏直接擷取的 wikiwiki.jp 清單。

來源之間有分歧時，問題會記錄在
`src/maeyomi/decoder/uncertainties.py`，連同每個來源的說法和所作的選擇。解碼器依循模擬器，除非曾在裝置上測試列印代碼的來源另有說法：高體力加成依循
[barcodebattler.net](https://barcodebattler.net/page21.htm) 和一份
[note.com 的分析](https://note.com/sakigomyway_5634/n/n61808a7245e5)，職業 6 則是戰士。在記錄的問題中，有五個會把未經驗證的數值印到卡片上，產生器拒絕輸出任何觸及它們的代碼。
