const LANGUAGES = ['en', 'ja'];
const LANGUAGE_KEY = 'maeyomi-language';

const MESSAGES = {
  en: {
    title: 'Maeyomi',
    lede:
      'Playable cards for Barcode Battler machines and barcode games, ' +
      'printed in English and Japanese.',
    'tabs.label': 'What would you like to make',
    'tab.one': 'One card',
    'tab.many': 'A sheet of cards',
    'tab.official': 'The real cards',
    'skip': 'Skip to the card maker',
    'tab.read': 'Read a barcode',
    'tab.cheat': 'Cheats',
    'cheat.note': 'The strongest cards the chosen machine or game will read, with every number at the most it allows. Print one kind, or every kind together.',
    'cheat.kind.all': 'Every kind together',
    'cheat.name.all': 'Each card is named after its kind. Pick one kind to give it a name of your own.',
    'status.cheatSheet': '{count} cheat cards the {device} will read.',
    'cheat.name': 'Name',
    'cheat.kind': 'Which cheats',
    'cheat.kind.hint': 'Each kind puts a different number, or every card of one kind, at the top.',
    'status.cheatMore': 'The sheet holds {count} cards.',
    'status.cheatKind': '{name}: {kind}, a cheat card the {device} will read.',
    'status.cheatKindOnly': '{kind}, a cheat card the {device} will read.',
    'cheat.name.hint': "Leave it empty for the card's own name. It does not change the barcode.",
    'cheat.preview': 'The cheat cards',
    'cheat.placeholder': 'The cards appear here.',
    'tab.shop': 'The supermarket',
    'shop.legend': 'Real Japanese groceries',
    'shop.query': 'Look for something',
    'shop.query.placeholder': 'tomato sauce',
    'shop.query.hint': 'Search by name, brand or barcode. Leave it empty to see the whole shelf.',
    'shop.note': 'Every one of these is a real product sold in Japan. The numbers on the card are not made up and are not theirs: this program reads them off the barcode, exactly as the machine does. Tomato sauce against noodles is a fair fight.',
    'shop.go': 'Search the shelf',
    'shop.surprise': 'Surprise me',
    'shop.pdf': 'Print what is listed',
    'shop.results': 'On the shelf',
    'shop.placeholder': 'Search for something, or press Surprise me.',
    'shop.empty': 'Nothing on the shelf matches that.',
    'shop.found': '{count} of {total} products.',
    'shop.credit': 'Product names and barcodes from {source}, under the {licence}.',
    'read.legend': 'Any barcode at all',
    'read.barcode': 'Barcode number',
    'read.placeholder': '4901085061169',
    'read.placeholder.code39': 'AA01C0RD00V01',
    'read.placeholder.code128': '011112884427',
    'read.note.card': 'This game reads only its own cards, so the barcode on a product is not one of them. Type the code printed under a card\'s bars to see which card it is.',
    'read.legend.card': 'The card\'s barcode',
    'read.barcode.hint.code39': 'The letters and digits printed under the bars. The stars at each end can be left out.',
    'read.barcode.hint.code128': 'The 12 digits printed under the bars.',
    'unavailable.shop.code39': 'This game reads Code 39 cards through its own reader, not the barcodes on the shopping, so nothing on the shelf is a card for it. Its cards are on The real cards, and any one of them can be printed from One card.',
    'unavailable.shop.code128': 'This game reads Code 128 cards through its own scanner, not the barcodes on the shopping, so nothing on the shelf is a card for it. Its cards are on The real cards, and any one of them can be printed from One card.',
    'unavailable.cheat': 'This game\'s cards carry no numbers, so no card is stronger than another and there is no cheat card. Its cards are on The real cards, and any one of them can be printed from One card.',
    'goto.official': 'See the real cards',
    'goto.one': 'Pick one card',
    'read.barcode.hint': 'The 8 or 13 digits printed under the bars. Spaces are fine.',
    'read.name': 'Name it',
    'read.name.placeholder': 'Tomato sauce',
    'read.name.hint': 'Printed on the card. The barcode decides everything else.',
    'read.note':
      'Any product barcode works, which is how the machine was played in 1992: a bottle of ' +
      'tomato sauce is a fighter, a packet of crisps is a weapon. Type what is printed on the ' +
      'shopping and see what comes out.',
    'read.go': 'Read it',
    'read.preview': 'What it is',
    'read.placeholder.card': 'Type a barcode and press Read it.',
    'read.empty': 'Type the digits printed under the bars first.',
    'read.ok': 'This is what the machine sees when you swipe it.',
    'read.refused': 'The machine will not read that one:',
    'fact.kind': 'Kind',
    'fact.class': 'Fights with',
    'fact.hp': 'Health',
    'fact.st': 'Attack',
    'fact.df': 'Defence',
    'fact.battle_st': 'Attack in battle',
    'fact.battle_df': 'Defence in battle',
    'fact.power': 'Special power',
    'fact.speed': 'Speed',
    'fact.reading': 'Read from',
    'reading.front': 'the front',
    'reading.back': 'the back',
    'one.who': 'Who is on the card',
    'one.name': 'Name',
    'one.name.hint': 'Printed on the card. It does not change the barcode.',
    'one.race': 'Kind of fighter',
    'one.class': 'Fights with',
    'class.either': 'Either',
    'class.warrior': 'A weapon, a warrior',
    'class.magician': 'Magic, a magician',
    'one.strong': 'How strong',
    'stat.hp': 'Health',
    'stat.st': 'Attack',
    'stat.df': 'Defence',
    'one.hpNote':
      'Above 20000 health the machine needs a marker in the barcode, so health has to end ' +
      'in 900 and speed is always 5. The slider snaps to the nearest one it can reach.',
    'one.abilityLegend': 'Special ability',
    'one.ability': 'Ability',
    'one.ability.hint':
      'The machine stores abilities as numbers. Only 00 to 49 work in an ordinary battle.',
    'one.detail': 'Fine detail',
    'one.speed': 'Speed, 0 to 9',
    'one.speed.hint': 'Decides who strikes first.',
    'one.job': 'Type',
    'one.job.hint': 'Some special powers hit only certain types.',
    'job.any': 'Any',
    'valid.number': 'Type a whole number.',
    'valid.range': 'Use a number from {min} to {max}.',
    'valid.step': 'Use a multiple of {step}.',
    'job.option': '{number}: {name}',
    'job.warrior': 'Warrior',
    'job.magician': 'Magician',
    'job.priest': 'Priest',
    'job.holy': 'Holy warrior',
    'one.back': 'Make a card the machine reads backwards',
    'one.back.hint': 'A backwards card carries other numbers: the sliders move to its limits.',
    'one.nearest': 'If those exact numbers are impossible, use the closest ones',
    'one.make': 'Make this card',
    download: 'Download to print',
    'one.preview': 'Your card',
    'one.placeholder': 'Your card appears here as you choose.',
    'one.more': 'More options',
    'device.super_famicom': 'Super Famicom, through the Barcode Battler II',
    'device.datach': 'Famicom Datach',
    'device.famicom': 'Famicom, through the Barcode Battler II',
    'one.code': 'Barcode number',
    copy: 'Copy',
    copied: 'Copied',
    any: 'any',
    'many.howMany': 'How many',
    'many.count': 'Cards',
    'many.count.hint': 'Nine fit on a page.',
    'many.seed': 'Batch number',
    'many.seed.placeholder': 'leave empty for a new set',
    'many.seed.hint': 'Use the same number to get the same cards again.',
    'many.range': 'Keep them in this range',
    to: 'to',
    'many.hpMax': 'Highest health',
    'many.stMax': 'Highest attack',
    'many.dfMax': 'Highest defence',
    'many.anyRace': 'Any kind',
    'many.make': 'Make the sheet',
    'many.preview': 'Your sheet',
    'many.placeholder': 'Press Make the sheet to see the pages.',
    'device.label': 'Machine or game',
    'device.change': 'Change',
    'device.filter': 'Find a machine or game',
    'device.machines': 'Machines',
    'device.summary.bb2': '1992. Fighters, items and cards read backwards.',
    'device.summary.bb1': '1991. Every fighter is a warrior; health stops at 19900.',
    'device.summary.double': '1993. Adds its own 7-read, priests and holy warriors.',
    'device.summary.dbz': 'Bandai, 1992. Fighters and items with BP and DP.',
    'device.summary.ultraman': 'Bandai, 1993. Ultra heroes, monsters and items with PW, ST and SP.',
    'device.summary.sdgundam': 'Bandai, 1993. Mobile suits with weapons, and command cards.',
    'device.summary.yuyu': 'Bandai, 1993. Fighters with their techniques, and items.',
    'device.summary.jleague': 'Bandai, 1994. The players and teams of the 1993 J.League.',
    'device.summary.barcodeworld': 'Sunsoft, 1992. Fighters read through a Barcode Battler 2.',
    'device.summary.senki': 'Epoch, 1993. A Super Famicom game read through a Barcode Battler 2.',
    'device.summary.lupin': 'Epoch, 1994. Codes on the password screen set off cheats and story routes.',
    'device.summary.donald': 'Epoch, 1995. Codes on the password screen open stages and endings.',
    'device.summary.spiderman': 'Epoch, 1995. Codes on the password screen set off cheats.',
    'device.summary.alice': 'Epoch, 1995. Codes on the password screen start the story later on.',
    'device.summary.doraemon2': 'Epoch, 1993. Codes set off cheats or give secret tools.',
    'device.summary.doraemon3': 'Epoch, 1994. Codes set off cheats or give weapons and items.',
    'device.summary.yousei': 'Epoch, 1993. Codes set off cheats or give gadgets.',
    'device.summary.excite95': "Epoch, 1995. Item cards that raise a player's ability for a match.",
    'device.summary.dslayer2': 'Epoch, 1993. Codes set off cheats or give items in the field.',
    'device.summary.bspace': 'Namco, 1992. Fighters read through the Barcode Boy.',
    'device.game_boy': 'Game Boy',
    'device.nintendo_ds': 'Nintendo DS',
    'official.note.bspace': '10 Battle Space cards are known.',
    'official.source.bspace': 'Battle Space cards:',
    'device.summary.monstmkb': 'Namco, 1993. Heroes for the party, read through the Barcode Boy.',
    'official.note.monstmkb': '8 Monster Maker barcodes are known. Each is named as the game shows it.',
    'official.source.monstmkb': 'Monster Maker cards:',
    'device.summary.kattobi': 'Namco, 1993. Racing cars read through the Barcode Boy.',
    'official.note.kattobi': 'Kattobi Road came with 6 cards. Each is named as the game shows it.',
    'official.source.kattobi': 'Kattobi Road cards:',
    'device.summary.famista3': 'Namco, 1993. Rookie batters and pitchers read through the Barcode Boy.',
    'official.note.famista3': 'Famista 3 came with 4 cards.',
    'official.source.famista3': 'Famista 3 cards:',
    'device.summary.famjock2': 'Namco, 1993. Racehorses, mares and stallions read through the Barcode Boy.',
    'device.summary.bardigun': 'Tamsoft, 1998. Barloid eggs hatched by the game\'s own reader.',
    'device.summary.cardasobu': 'Sega, 2007. Kana cards read through Sega\'s HCV-1000 card reader.',
    'device.summary.osharemajo': 'Sega, 2006. Love and Berry arcade cards read through the HCV-1000.',
    'device.summary.mushiking': 'Sega, 2007. Mushiking arcade cards read through the HCV-1000.',
    'official.note.mushiking': 'Every card the game reads: 535 beetle, partner, move, license and extra cards from its own lists. Each was matched by the game\'s own comparison.',
    'official.source.mushiking': 'Mushiking cards:',
    'device.summary.wantame': 'Capcom, 2007. Wantame Code 128 cards read through a scanner on the microphone.',
    'official.note.wantame': 'Every card the game takes: 235 dog, outfit, accessory and effect cards from its own tables. Each was found by the game\'s own checks.',
    'official.source.wantame': 'Wantame cards:',
    'official.note.osharemajo': 'Every item the game keeps a card image for and a card can give: 281 dresses, hairstyles, shoes and special cards. Each was read by the game\'s own decoder.',
    'official.source.osharemajo': 'Oshare Majo cards:',
    'official.note.famjock2': 'Family Jockey 2 came with 8 cards. Five give other numbers than the ones printed on them; these print what the game reads.',
    'official.source.famjock2': 'Family Jockey 2 cards:',
    'official.note.cardasobu': 'Card de Asobu came with 46 cards, one for each kana and one that starts the card search. Each was read by the game.',
    'official.source.cardasobu': 'Card de Asobu cards:',
    'official.source.famjock2.errors': 'Which cards give other numbers:',
    'device.summary.hatayama': 'Epoch, 1993. Battlers with stamina, attack, defense and magic.',
    'device.summary.excite94': 'Epoch, 1994. 240 hidden players and item cards for a match.',
    'device.summary.battlerush': 'Bandai, 1993. A robot built from two cards read in order.',
    'device.hint':
      'Every tab makes cards for this choice and reads barcodes its way. ' +
      'The same barcode is a different card on each one.',
    'stat.bp': 'Battle power',
    'stat.dp': 'Defence power',
    'dbz.character': 'Fighter or item',
    'dbz.character.hint':
      'A fighter whose numbers are high enough turns into its stronger form, as the game ' +
      'does. An item carries no numbers.',
    'dbz.anyone': 'Any fighter',
    'dbz.fighters': 'Fighters',
    'dbz.items': 'Items',
    'dbz.level': 'Special move level',
    'dbz.level.any': 'Any',
    'game.character': 'Card',
    'game.character.hint': "The game reads the card by its number in the game's own list.",
    'game.anyone': 'Any card',
    'game.kind.fighter': 'Fighters',
    'game.kind.item': 'Items',
    'stat.pw': 'PW',
    'stat.ust': 'ST',
    'stat.usp': 'SP',
    'stat.ap': 'AP',
    'stat.gdp': 'DP',
    'stat.yhp': 'HP',
    'stat.ysp': 'SP',
    'game.kind.hidden': 'Hidden',
    'game.kind.team': 'Teams',
    'game.kind.player': 'Players',
    'stat.whp': 'Health',
    'stat.wst': 'Attack',
    'stat.wdf': 'Defence',
    'game.kind.unit': 'Mobile suits',
    'game.kind.command': 'Command cards',
    'game.pick.any': 'Any',
    'status.deviceCard': 'This card reads exactly as asked on the {device}.',
    'status.deviceCheat': '{name}: the strongest card the {device} will read.',
    'status.searching': 'Looking for a barcode the {device} reads this way.',
    'status.deviceClosest': 'Those exact numbers cannot be printed, so this is the closest card that can.',
    'official.legend': 'Cards that were really sold',
    'official.single': '{title} ({count} cards)',
    'official.single.one': '{title} (1 card)',
    'official.set': 'Which set',
    'official.note.epoch':
      'Epoch never published a list of its cards, so these barcodes were typed in by ' +
      'collectors on a Japanese fan wiki about the Barcode Battler, hosted on wikiwiki.jp. ' +
      'The numbers on every card are read from its barcode by this program, never copied ' +
      'from the wiki.',
    'official.note.dbz':
      'Datach Dragon Ball Z came with 40 cards, and its manual says some of them, such as ' +
      'Super Saiyan Goku and Perfect Cell, carry no barcode: players stuck one of their own on ' +
      'them. The 35 that carry one, plus a special Super Saiyan Goku card, are the 36 here, ' +
      'taken from the card list in the source code of puNES, a Famicom emulator, and each read ' +
      'by the game itself in the MAME emulator. The numbers on every card come from its barcode.',
    'official.sources': 'Where the barcodes come from',
    'official.source.epoch': 'Epoch cards:',
    'official.source.dbz': 'Dragon Ball Z cards:',
    'official.note.ultraman':
      'Datach Ultraman Club came with 40 cards, two of them blank. The 38 with a barcode ' +
      'were read off a boxed set by retrostuff.org, are named as the card list in the source ' +
      'code of puNES, a Famicom emulator, names them, and were each read by the game itself in ' +
      'the MAME emulator. The numbers on every card come from its barcode.',
    'official.source.ultraman': 'Ultraman Club cards:',
    'official.note.sdgundam':
      'SD Gundam Wars came with 40 cards. 37 of them carry two barcodes, a mobile suit on the ' +
      'bottom edge and a command on the top, plus a special card with one of each. The 76 ' +
      'barcodes were read off a boxed set by retrostuff.org, match the card list in the ' +
      'source code of puNES, a Famicom emulator, and were each read by the game itself in ' +
      'the MAME emulator.',
    'official.source.sdgundam': 'SD Gundam Wars cards:',
    'official.note.yuyu':
      'Yu Yu Hakusho came with 40 cards, three of them without a barcode. The other 37 come ' +
      'from the spreadsheet archive.org keeps beside its scans of a complete set, and were ' +
      'each read by the game itself in the MAME emulator.',
    'official.source.yuyu': 'Yu Yu Hakusho cards:',
    'official.note.jleague':
      'J.League Super Top Players came with 40 cards, each with four barcodes: a team and ' +
      'three players, or four players. The 160 barcodes come from the spreadsheet archive.org ' +
      'keeps beside its scans of a complete set, and each was read by the game itself in the ' +
      'MAME emulator. A card names a real player and carries no numbers of its own.',
    'official.source.jleague': 'J.League cards:',
    'official.note.barcodeworld':
      'Barcode World came with 24 cards and a blank white one. Their barcodes were read off ' +
      'the card scans barcodebattler.co.uk publishes, and each was read by the game itself in ' +
      'the MAME emulator. Weapons, protectors and items are scanned during a battle, not at ' +
      'the character screen.',
    'official.source.barcodeworld': 'Barcode World cards:',
    'official.note.senki':
      'Barcode Battler Senki came with 10 cards: 5 characters, 3 items and 2 blank white ' +
      'ones. Nobody has published their barcodes, so there is no set to print. Any card made ' +
      'here is read by the game the way it was checked in the MAME emulator.',
    'official.source.senki': 'What came in the Senki box:',
    'official.note.excite95':
      'Epoch printed a roster card for each of the 12 J.League clubs of 1994 for Excite Stage ' +
      "'94. Excite Stage '95 reads each one as an item card. The barcodes were read off the scans " +
      'barcodebattler.co.uk publishes, and each was read by the game in the MAME emulator.',
    'official.source.excite95': 'Club roster cards:',
    'official.note.excite94':
      'Epoch printed a roster card for each of the 12 J.League clubs of 1994 for this game. ' +
      'Each reads as an item card. The barcodes were read off the scans barcodebattler.co.uk ' +
      'publishes, and each was read by the game in the MAME emulator.',
    'official.source.excite94': 'Club roster cards:',
    'official.note.battlerush':
      'No list of the cards Bandai printed for Battle Rush is known. Each robot made here ' +
      'prints as two cards, scanned in order at the Robo Factory.',
    'official.note.hatayama':
      'Hatayama Hatch came with cards for 12 real teams and 2 of its own, and nobody has ' +
      'published their barcodes.',
    'official.note.effects':
      'No card is known to have come with this game: its manual names none and tells you to ' +
      'try any barcode. Each code made here names the screen to scan it on, and was seen ' +
      'setting off its effect there in the MAME emulator.',
    'official.note.alice':
      'No card is known to have come with this game: its manual names none and says the ' +
      'game takes only the numbers it sets in advance. Each code made here is one of them, ' +
      'names the screen to scan it on, and was seen setting off its effect there in the ' +
      'MAME emulator.',
    'official.note.doraemon':
      'No record says this game came with cards, and nobody has published which barcodes do ' +
      'what in it. Each code made here was found in the game itself, names the screen to ' +
      'scan it on, and was seen setting off its effect there in the MAME emulator.',
    'official.note.yousei':
      'No record says this game came with cards. A known trick scans the barcode on the ' +
      'game\'s own box, but that number is not known here, so it is not offered. Each code ' +
      'made here names the screen to scan it on, and was seen setting off its effect there ' +
      'in the MAME emulator.',
    'official.note.dslayer2':
      'No record says this game came with cards. It reads Selios, a card of the separately ' +
      'sold Barcode Battler II pack Dragon Slayer: The Legend of Heroes, and raises every ' +
      'status of the hero to its highest; that card prints below. A known trick also scans ' +
      'the barcode on the Barcode Battler II\'s own box, but that number is not known here, ' +
      'so it is not offered. Each code made here names the screen to scan it on, and was ' +
      'seen setting off its effect there in the MAME emulator.',
    'official.source.manual':
      'The game\'s manual:',
    'official.source.dslayer2':
      'The Selios card and what it does:',
    'official.source.yousei':
      'The box barcode trick:',
    'official.skipped': 'Cards left out',
    'official.skipped.hint':
      'The last digit of a barcode is a check digit worked out from the other twelve, so a ' +
      'mistyped digit on the wikiwiki.jp page shows up. Where the numbers that page gives ' +
      'for the card point to one digit, the card is repaired and printed. No single repair ' +
      'fits the numbers of the cards below, so they are left out rather than guessed.',
    'official.show': 'Show the cards',
    'official.preview': 'The set',
    'official.placeholder': 'Pick a set and press Show the cards.',
    'official.every': 'Every set, {count} cards',
    'official.option': '{title}, {count} cards',
    'official.option.one': '{title}, 1 card',
    'official.inJapanese': 'In Japanese: {title}',
    'official.everyHint': 'Every card from every set, one after another.',
    'footer.local': 'Nothing leaves this machine. The page talks to a server you started.',
    'tag.exact': 'Exact',
    'tag.closest': 'Closest',
    'tag.impossible': 'Not possible',
    'tag.ready': 'Ready',
    'tag.working': 'Working',
    'tag.done': 'Done',
    'tag.cheat': 'Cheat',
    'status.exact': 'The machine will read exactly these numbers.',
    'status.closest':
      'Those exact numbers are impossible on this machine. This is the nearest card.',
    'status.adjust': 'Try adjusting:',
    'status.again': 'Try again:',
    'status.wrong': 'Something went wrong. Please try different numbers.',
    'status.sheet': '{count} cards across {pages} pages.',
    'status.sheetOne': '{count} cards on 1 page.',
    'status.drawing': 'Drawing the cards...',
    'status.building': 'Building the file. A big set takes a moment.',
    'status.saved': 'The file is in your downloads.',
    'status.official': '{count} cards.',
    'status.officialMore':
      '{count} cards. The first {shown} are shown here; the download has all of them.',
    'alt.card': 'The card for {name}, showing its numbers and barcode',
    'alt.page': '{label}, page {page}',
    'alt.single': '{label}: the one card, as it prints',
    'label.sheet': 'Sheet',
    'label.official': 'Official cards',
    wrong: [
      'Nice try. The machine is not impressed.',
      'Nope. Maybe ask a grown-up who played in 1992?',
      'That is not it. The machine yawns.',
    ],
  },
  ja: {
    title: 'Maeyomi',
    lede:
      'バーコードバトラーや バーコードで あそぶ ゲームの カードを、' +
      'えいごと にほんごで いんさつしよう。',
    'tabs.label': 'なにを つくる？',
    'tab.one': 'カード 1まい',
    'tab.many': 'カードを まとめて',
    'tab.official': 'ほんものの カード',
    'skip': 'カードづくりへ とぶ',
    'tab.read': 'バーコードを よむ',
    'tab.cheat': 'チート',
    'cheat.note': 'えらんだ マシンや ゲームが よめる いちばん つよい カード。どの すうじも いちばん おおきく なるよ。1しゅるいでも、ぜんぶ いっしょでも いんさつ できるよ。',
    'cheat.name': 'なまえ',
    'cheat.kind': 'どの チート',
    'cheat.kind.hint': 'しゅるいごとに ちがう すうじや、おなじ しゅるいの カード ぜんぶが いちばん つよく なるよ。',
    'status.cheatMore': 'シートには {count}まいの カードが はいるよ。',
    'status.cheatKind': '{name}: {device} の チートカード、{kind}。',
    'status.cheatKindOnly': '{device} の チートカード、{kind}。',
    'cheat.name.hint': 'からっぽなら カードの なまえの まま。バーコードは かわらないよ。',
    'cheat.preview': 'チートカード',
    'cheat.placeholder': 'ここに カードが でるよ。',
    'cheat.kind.all': 'ぜんぶ いっしょに',
    'cheat.name.all': 'カードは それぞれ しゅるいの なまえに なるよ。じぶんで なまえを つけるなら しゅるいを 1つ えらんでね。',
    'status.cheatSheet': '{device} が よめる チートカード {count}まい。',
    'tab.shop': 'スーパーマーケット',
    'shop.legend': 'ほんものの 日本の しょくひん',
    'shop.query': 'さがしてみよう',
    'shop.query.placeholder': 'トマトソース',
    'shop.query.hint': 'なまえ・ブランド・バーコードで さがせます。からっぽだと ぜんぶ でます。',
    'shop.note': 'ここにあるのは ぜんぶ 日本で うっている ほんものの しょうひんです。カードの すうじは かってに つくったものでも、メーカーの ものでも ありません。このプログラムが バーコードから よみとった すうじです。トマトソース たい ラーメンも まじめな しょうぶです。',
    'shop.go': 'たなを さがす',
    'shop.surprise': 'おまかせ',
    'shop.pdf': 'この リストを いんさつ',
    'shop.results': 'たなの なかみ',
    'shop.placeholder': 'なにか さがすか、おまかせを おしてください。',
    'shop.empty': 'それに あう しょうひんは ありません。',
    'shop.found': '{total}こ のうち {count}こ。',
    'shop.credit': 'しょうひんめいと バーコードは {source}（{licence}）より。',
    'read.legend': 'どんな バーコードでも',
    'read.barcode': 'バーコード ばんごう',
    'read.placeholder': '4901085061169',
    'read.placeholder.code39': 'AA01C0RD00V01',
    'read.placeholder.code128': '011112884427',
    'read.note.card': 'この ゲームは じぶんの カードしか よまないので、しょうひんの バーコードは カードに ならない。カードの バーの したの コードを いれると、どの カードか わかる。',
    'read.legend.card': 'カードの バーコード',
    'read.barcode.hint.code39': 'バーの したに かいてある えいじと すうじ。りょうはしの ほしは なくても だいじょうぶ。',
    'read.barcode.hint.code128': 'バーの したに かいてある 12けたの すうじ。',
    'unavailable.shop.code39': 'この ゲームは じぶんの リーダーで Code 39 の カードを よむので、かいものの バーコードは カードに ならない。ゲームの カードは「ほんものの カード」に あり、どれでも「カード 1まい」から いんさつ できる。',
    'unavailable.shop.code128': 'この ゲームは じぶんの スキャナーで Code 128 の カードを よむので、かいものの バーコードは カードに ならない。ゲームの カードは「ほんものの カード」に あり、どれでも「カード 1まい」から いんさつ できる。',
    'unavailable.cheat': 'この ゲームの カードには すうじが ないので、ほかより つよい カードは なく、チートカードも ない。ゲームの カードは「ほんものの カード」に あり、どれでも「カード 1まい」から いんさつ できる。',
    'goto.official': 'ほんものの カードを みる',
    'goto.one': 'カードを 1まい えらぶ',
    'read.barcode.hint': 'バーの したに かいてある 8けた か 13けた。スペースが あっても だいじょうぶ。',
    'read.name': 'なまえを つける',
    'read.name.placeholder': 'トマトソース',
    'read.name.hint': 'カードに いんさつされます。ほかは ぜんぶ バーコードが きめます。',
    'read.note':
      'どんな しょうひんの バーコードでも つかえます。1992ねんの あそびかたは これでした。' +
      'トマトソースの ビンが せんしに なり、おかしの ふくろが ぶきに なります。' +
      'かいものの バーコードを うちこんで なにが でるか みてね。',
    'read.go': 'よみとる',
    'read.preview': 'なにに なった？',
    'read.placeholder.card': 'バーコードを いれて「よみとる」を おしてね。',
    'read.empty': 'まず バーの したの すうじを いれてね。',
    'read.ok': 'これが マシンに とおした ときに みえる すがたです。',
    'read.refused': 'マシンは これを よみとれません:',
    'fact.kind': 'しゅるい',
    'fact.class': 'たたかいかた',
    'fact.hp': 'たいりょく',
    'fact.st': 'こうげき',
    'fact.df': 'ぼうぎょ',
    'fact.battle_st': 'たたかいの こうげき',
    'fact.battle_df': 'たたかいの ぼうぎょ',
    'fact.power': 'とくしゅのうりょく',
    'fact.speed': 'スピード',
    'fact.reading': 'よみかた',
    'reading.front': 'まえから',
    'reading.back': 'うしろから',
    'one.who': 'カードに のる キャラクター',
    'one.name': 'なまえ',
    'one.name.hint': 'カードに いんさつされます。バーコードは かわりません。',
    'one.race': 'しゅぞく',
    'one.class': 'たたかいかた',
    'class.either': 'どちらでも',
    'class.warrior': 'ぶきで たたかう せんし',
    'class.magician': 'まほうで たたかう まほうつかい',
    'one.strong': 'つよさ',
    'stat.hp': 'たいりょく',
    'stat.st': 'こうげき',
    'stat.df': 'ぼうぎょ',
    'one.hpNote':
      'たいりょくが 20000 を こえると、バーコードに しるしが ひつようです。' +
      'たいりょくは 900 で おわり、スピードは いつも 5 に なります。スライダーは つくれる あたいに あわせます。',
    'one.abilityLegend': 'とくしゅのうりょく',
    'one.ability': 'のうりょく',
    'one.ability.hint':
      'マシンは のうりょくを ばんごうで おぼえます。ふつうの たたかいで つかえるのは 00〜49 だけです。',
    'one.detail': 'くわしい せってい',
    'one.speed': 'スピード (0〜9)',
    'one.speed.hint': 'どちらが さきに こうげき するかを きめます。',
    'one.job': 'しょくぎょう',
    'one.job.hint': 'とくしゅ のうりょくには きまった しょくぎょうにだけ きく ものが あります。',
    'job.any': 'どれでも',
    'valid.number': 'すうじを いれてね。',
    'valid.range': '{min} から {max} までの すうじに してね。',
    'valid.step': '{step} ずつの すうじに してね。',
    'job.option': '{number}: {name}',
    'job.warrior': 'せんし',
    'job.magician': 'まほうつかい',
    'job.priest': 'そうりょ',
    'job.holy': 'せいせんし',
    'one.back': 'マシンが うしろから よむ カードに する',
    'one.back.hint': 'うしろから よむ カードは すうじの はんいが ちがうので、スライダーが その はんいに かわります。',
    'one.nearest': 'その すうじが つくれない ときは、いちばん ちかい カードに する',
    'one.make': 'カードを つくる',
    download: 'いんさつようを ダウンロード',
    'one.preview': 'あなたの カード',
    'one.placeholder': 'えらぶと ここに カードが でるよ。',
    'one.more': 'ほかの せってい',
    'device.super_famicom': 'スーパーファミコン、バーコードバトラーII で よむ',
    'device.datach': 'ファミコン データック',
    'device.famicom': 'ファミコン、バーコードバトラーII で よむ',
    'one.code': 'バーコード ばんごう',
    copy: 'コピー',
    copied: 'コピー しました',
    any: 'なんでも',
    'many.howMany': 'なんまい',
    'many.count': 'まいすう',
    'many.count.hint': '1ページに 9まい はいります。',
    'many.seed': 'セット ばんごう',
    'many.seed.placeholder': 'からっぽなら あたらしい セット',
    'many.seed.hint': 'おなじ ばんごうなら おなじ カードが また できます。',
    'many.range': 'この はんいで つくる',
    to: '〜',
    'many.hpMax': 'たいりょくの さいだい',
    'many.stMax': 'こうげきの さいだい',
    'many.dfMax': 'ぼうぎょの さいだい',
    'many.anyRace': 'どの しゅぞくでも',
    'many.make': 'まとめて つくる',
    'many.preview': 'あなたの シート',
    'many.placeholder': '「まとめて つくる」を おすと ページが みられます。',
    'device.label': 'つかう マシン・ゲーム',
    'device.change': 'かえる',
    'device.filter': 'マシンや ゲームを さがす',
    'device.machines': 'マシン',
    'device.summary.bb2': '1992ねん。キャラクター、アイテム、うしろから よむ カード。',
    'device.summary.bb1': '1991ねん。ぜんいん せんし。たいりょくは 19900 まで。',
    'device.summary.double': '1993ねん。7よみ、そうりょ、せいせんし が ふえた。',
    'device.summary.dbz': 'バンダイ、1992ねん。BP と DP の キャラクターと アイテム。',
    'device.summary.ultraman': 'バンダイ、1993ねん。PW、ST、SP の ウルトラヒーロー、かいじゅう、アイテム。',
    'device.summary.sdgundam': 'バンダイ、1993ねん。ぶきを もつ モビルスーツと コマンドカード。',
    'device.summary.yuyu': 'バンダイ、1993ねん。わざを もつ キャラクターと アイテム。',
    'device.summary.jleague': 'バンダイ、1994ねん。1993ねんの Jリーグの せんしゅと チーム。',
    'device.summary.barcodeworld': 'サンソフト、1992ねん。バーコードバトラー2 で よむ キャラクター。',
    'device.summary.senki': 'エポックしゃ、1993ねん。バーコードバトラー2 で よむ スーパーファミコンの ゲーム。',
    'device.summary.lupin': 'エポックしゃ、1994ねん。パスワード がめんの コードで うらわざと ルート。',
    'device.summary.donald': 'エポックしゃ、1995ねん。パスワード がめんの コードで ステージと エンディング。',
    'device.summary.spiderman': 'エポックしゃ、1995ねん。パスワード がめんの コードで うらわざ。',
    'device.summary.alice': 'エポックしゃ、1995ねん。パスワード がめんの コードで おはなしの とちゅうから。',
    'device.summary.doraemon2': 'エポックしゃ、1993ねん。コードで うらわざや ひみつどうぐ。',
    'device.summary.doraemon3': 'エポックしゃ、1994ねん。コードで うらわざや ぶき、アイテム。',
    'device.summary.yousei': 'エポックしゃ、1993ねん。コードで うらわざや どうぐ。',
    'device.summary.excite95': 'エポックしゃ、1995ねん。しあいで せんしゅの のうりょくを あげる アイテム カード。',
    'device.summary.dslayer2': 'エポックしゃ、1993ねん。コードで うらわざや フィールドの アイテム。',
    'device.summary.bspace': 'ナムコ、1992ねん。バーコードボーイで よむ せんし。',
    'device.game_boy': 'ゲームボーイ',
    'device.nintendo_ds': 'ニンテンドーDS',
    'official.note.bspace': 'バトルスペース の カード は 10まい しられています。',
    'official.source.bspace': 'バトルスペースの カード:',
    'device.summary.monstmkb': 'ナムコ、1993ねん。バーコードボーイで よむ パーティー の ゆうしゃ。',
    'official.note.monstmkb': 'モンスターメーカー の バーコード は 8つ しられています。なまえ は ゲーム の ひょうじ の とおり です。',
    'official.source.monstmkb': 'モンスターメーカーの カード:',
    'device.summary.kattobi': 'ナムコ、1993ねん。バーコードボーイで よむ レースカー。',
    'official.note.kattobi': 'カットビロード には 6まいの カードが ついていました。なまえ は ゲーム の ひょうじ の とおり です。',
    'official.source.kattobi': 'カットビロードの カード:',
    'device.summary.famista3': 'ナムコ、1993ねん。バーコードボーイで よむ ルーキーの バッターと ピッチャー。',
    'official.note.famista3': 'ファミスタ3 には 4まいの カードが ついていました。',
    'official.source.famista3': 'ファミスタ3の カード:',
    'device.summary.famjock2': 'ナムコ、1993ねん。バーコードボーイで よむ 競走馬、繁殖馬、種馬。',
    'device.summary.bardigun': 'タムソフト、1998ねん。ゲームに ついている リーダーで タマゴを かえす バーロイド。',
    'device.summary.cardasobu': 'セガ、2007ねん。セガの カードリーダー HCV-1000で よむ かなの カード。',
    'device.summary.osharemajo': 'セガ、2006ねん。HCV-1000で よむ ラブandベリーの アーケードカード。',
    'device.summary.mushiking': 'セガ、2007ねん。HCV-1000で よむ ムシキングの アーケードカード。',
    'official.note.mushiking': 'ゲームが よむ カード ぜんぶ、535まいの ムシ、パートナー、わざ、ライセンス、とくべつの カードです。どれも ゲームの くらべかたで たしかめました。',
    'official.source.mushiking': 'ムシキングの カード:',
    'device.summary.wantame': 'カプコン、2007ねん。マイクに つなぐ スキャナーで よむ ワンタメの Code 128 カード。',
    'official.note.wantame': 'ゲームが うけとる カード ぜんぶ、235まいの いぬ、ふく、アクセサリ、エフェクトの カードです。どれも ゲームの チェックで たしかめました。',
    'official.source.wantame': 'ワンタメの カード:',
    'official.note.osharemajo': 'ゲームが カードの えを もっていて、カードで もらえる アイテム ぜんぶ、281まいの ドレス、ヘア、くつ、スペシャルです。どれも ゲームの デコーダで よめることを たしかめました。',
    'official.source.osharemajo': 'オシャレ魔女の カード:',
    'official.note.famjock2': 'ファミリージョッキー2 には 8まいの カードが ついていました。5まいは カードに かかれた かずとは ちがう かずに なります。ここでは ゲームが よむ とおりに いんさつします。',
    'official.source.famjock2': 'ファミリージョッキー2の カード:',
    'official.note.cardasobu': 'カードであそぶには 46まいの カードが ついていました。かな ひとつに 1まいと、カードさがしを はじめる 1まいです。どれも ゲームで よめることを たしかめました。',
    'official.source.cardasobu': 'カードであそぶの カード:',
    'official.source.famjock2.errors': 'ちがう かずに なる カード:',
    'device.summary.hatayama': 'エポックしゃ、1993ねん。たいりょく、こうげき、ぼうぎょ、まほうの バトラー。',
    'device.summary.excite94': 'エポックしゃ、1994ねん。240にんの かくし せんしゅと しあいの アイテム カード。',
    'device.summary.battlerush': 'バンダイ、1993ねん。じゅんに よませる 2まいの カードで つくる ロボット。',
    'device.hint':
      'どの タブも、ここで えらんだ ものの カードを つくり、その よみかたで バーコードを よみます。' +
      'おなじ バーコードでも マシンや ゲームごとに ちがう カードに なります。',
    'stat.bp': 'せんとうりょく',
    'stat.dp': 'ぼうぎょりょく',
    'dbz.character': 'キャラクター・アイテム',
    'dbz.character.hint':
      'すうじが じゅうぶん たかい キャラクターは、ゲームと おなじように つよい すがたに へんしんします。' +
      'アイテムには すうじが ありません。',
    'dbz.anyone': 'だれでも',
    'dbz.fighters': 'キャラクター',
    'dbz.items': 'アイテム',
    'dbz.level': 'ひっさつわざ レベル',
    'dbz.level.any': 'どれでも',
    'game.character': 'カード',
    'game.character.hint': 'ゲームは カードを ゲームの なかの いちらんの ばんごうで よみます。',
    'game.anyone': 'どれでも',
    'game.kind.fighter': 'キャラクター',
    'game.kind.item': 'アイテム',
    'stat.pw': 'PW',
    'stat.ust': 'ST',
    'stat.usp': 'SP',
    'stat.ap': 'AP',
    'stat.gdp': 'DP',
    'stat.yhp': 'HP',
    'stat.ysp': 'SP',
    'game.kind.hidden': 'かくし',
    'game.kind.team': 'チーム',
    'game.kind.player': 'せんしゅ',
    'stat.whp': 'たいりょく',
    'stat.wst': 'こうげきりょく',
    'stat.wdf': 'しゅびりょく',
    'game.kind.unit': 'モビルスーツ',
    'game.kind.command': 'コマンドカード',
    'game.pick.any': 'どれでも',
    'status.deviceCard': '{device} で ちゅうもん どおりに よめる カードです。',
    'status.deviceCheat': '{name}: {device} が よめる いちばん つよい カード。',
    'status.searching': '{device} が こう よむ バーコードを さがしています。',
    'status.deviceClosest': 'その すうじ ぴったりの カードは つくれないので、いちばん ちかい カードに しました。',
    'official.legend': 'ほんとうに うられた カード',
    'official.single': '{title}（{count}まい）',
    'official.single.one': '{title}（1まい）',
    'official.set': 'どの シリーズ',
    'official.note.epoch':
      'エポック社は カードの いちらんを こうかいしていません。そこで バーコードは、wikiwiki.jp に ある ' +
      'バーコードバトラーの ファン wiki に コレクターが かきうつした ものを つかっています。' +
      'カードの すうじは この プログラムが バーコードから よみとった もので、wiki から ' +
      'うつした ものでは ありません。',
    'official.note.dbz':
      'データック ドラゴンボールZ には 40まいの カードが ついていて、せつめいしょに よると ' +
      'スーパーサイヤ人の 悟空や 完全体の セルなど いくつかには バーコードが なく、じぶんで ' +
      'バーコードを はって つかいました。バーコードの ある 35まいと、とくべつな スーパーサイヤ人の ' +
      '悟空の カードが ここの 36まいで、エミュレーター puNES の ソースコードの いちらんから とり、' +
      '1まいずつ MAME で ゲームに よませて たしかめました。',
    'official.sources': 'バーコードの でどころ',
    'official.source.epoch': 'エポック社の カード:',
    'official.source.dbz': 'ドラゴンボールZ の カード:',
    'official.note.ultraman':
      'データック ウルトラマン倶楽部 には 40まいの カードが ついていて、2まいは まっしろです。' +
      'バーコードの ある 38まいは retrostuff.org が はこいりの セットから よみとった もので、' +
      'なまえは エミュレーター puNES の ソースコードの いちらんから とり、1まいずつ MAME で ' +
      'ゲームに よませて たしかめました。',
    'official.source.ultraman': 'ウルトラマン倶楽部 の カード:',
    'official.note.sdgundam':
      'SDガンダム ガンダムウォーズ の 40まいの カードの うち 37まいには、したに モビルスーツ、' +
      'うえに コマンドの 2つの バーコードが あり、ほかに とくべつな カードが 1まい あります。' +
      '76この バーコードは retrostuff.org が はこいりの セットから よみとった もので、' +
      'エミュレーター puNES の いちらんと おなじで、1こずつ MAME で ゲームに よませて たしかめました。',
    'official.source.sdgundam': 'SDガンダム の カード:',
    'official.note.yuyu':
      '幽遊白書 には 40まいの カードが ついていて、3まいには バーコードが ありません。' +
      'のこりの 37まいは archive.org に ある ぜんセットの スキャンに そえられた ひょうから とり、' +
      '1まいずつ MAME で ゲームに よませて たしかめました。',
    'official.source.yuyu': '幽遊白書 の カード:',
    'official.note.jleague':
      'Jリーグ スーパートッププレイヤーズ には 40まいの カードが ついていて、1まいに 4つの ' +
      'バーコードが あります。160この バーコードは archive.org に ある ぜんセットの スキャンに ' +
      'そえられた ひょうから とり、1こずつ MAME で ゲームに よませて たしかめました。' +
      'カードは ほんものの せんしゅを えらぶだけで、じぶんの すうじは もちません。',
    'official.source.jleague': 'Jリーグ の カード:',
    'official.note.barcodeworld':
      'バーコードワールド には 24まいの カードと まっしろな カードが 1まい ついていました。' +
      'バーコードは barcodebattler.co.uk が こうかいしている カードの スキャンから よみとり、' +
      '1まいずつ MAME で ゲームに よませて たしかめました。ぶき・ぼうぐ・アイテムは ' +
      'キャラクターの がめんでは なく、たたかいの とちゅうで とおします。',
    'official.source.barcodeworld': 'バーコードワールド の カード:',
    'official.note.senki':
      'バーコードバトラー戦記 には 10まいの カードが ついていました。キャラクター 5まい、アイテム 3まい、' +
      'まっしろな カード 2まいです。その バーコードは だれも こうかいしていないので、いんさつできる ' +
      'シリーズは ありません。ここで つくる カードは、MAME で たしかめた とおりに ゲームが よみます。',
    'official.source.senki': 'バーコードバトラー戦記 の はこの なかみ:',
    'official.note.excite95':
      "エポックしゃは エキサイトステージ'94 の ために、1994ねんの Jリーグ 12クラブの " +
      "とうろく せんしゅ リストの カードを つくりました。エキサイトステージ'95 は それぞれを " +
      'アイテム カードとして よみます。バーコードは barcodebattler.co.uk の スキャンから よみとり、' +
      '1まいずつ MAME で ゲームに よませました。',
    'official.source.excite95': 'クラブの カード:',
    'official.note.excite94':
      'エポックしゃは この ゲームの ために、1994ねんの Jリーグ 12クラブの とうろく せんしゅ ' +
      'リストの カードを つくりました。どれも アイテム カードとして よまれます。バーコードは ' +
      'barcodebattler.co.uk の スキャンから よみとり、1まいずつ MAME で ゲームに よませました。',
    'official.source.excite94': 'クラブの カード:',
    'official.note.battlerush':
      'バンダイが バトルラッシュ に つけた カードの いちらんは しられていません。ここで つくる ' +
      'ロボットは 2まいの カードに なり、ロボ こうじょうで じゅんに よませます。',
    'official.note.hatayama':
      'はた山ハッチの パロ野球ニュース には じっさいの 12チームと オリジナルの 2チームの ' +
      'カードが ついていましたが、その バーコードは だれも こうかいしていません。',
    'official.note.effects':
      'この ゲームに カードが ついていた という きろくは ありません。せつめいしょにも カードは なく、いろいろな バーコードを ためすように かいてあります。ここで ' +
      'つくる コードには よませる がめんが かいてあり、MAME で そこで こうかが でることを たしかめました。',
    'official.note.alice':
      'この ゲームに カードが ついていた という きろくは ありません。せつめいしょにも カードは なく、ゲームで きめてある ばんごう しか うけつけないと ' +
      'かいてあります。ここで つくる コードは その ばんごうで、よませる がめんが かいてあり、MAME で そこで こうかが でることを たしかめました。',
    'official.note.doraemon':
      'この ゲームに カードが ついていた という きろくは なく、どの バーコードで なにが おきるかも こうかいされていません。ここで つくる コードは ゲームの ' +
      'なかから みつけた もので、よませる がめんが かいてあり、MAME で そこで こうかが でることを たしかめました。',
    'official.note.yousei':
      'この ゲームに カードが ついていた という きろくは ありません。ゲームの はこの バーコードを よませる うらわざが しられていますが、その ばんごうは ここでは ' +
      'わからないので のせていません。ここで つくる コードには よませる がめんが かいてあり、MAME で そこで こうかが でることを たしかめました。',
    'official.note.dslayer2':
      'この ゲームに カードが ついていた という きろくは ありません。べつうりの バーコードバトラーII の カード「ドラゴンスレイヤー英雄伝説」の セリオスを ' +
      'よませると、しゅじんこうの のうりょくが すべて さいだいに なります。その カードは したで いんさつできます。バーコードバトラーII の はこの バーコードを ' +
      'つかう うらわざも しられていますが、その ばんごうは ここでは わからないので のせていません。ここで つくる コードには よませる がめんが かいてあり、MAME ' +
      'で そこで こうかが でることを たしかめました。',
    'official.source.manual':
      'ゲームの せつめいしょ:',
    'official.source.dslayer2':
      'セリオスの カードと その こうか:',
    'official.source.yousei':
      'はこの バーコードの うらわざ:',
    'official.skipped': 'のぞいた カード',
    'official.skipped.hint':
      'バーコードの さいごの けたは ほかの 12けたから けいさんする チェック用の すうじなので、' +
      'wikiwiki.jp の ページの うちまちがいが わかります。ページに のっている カードの すうじから ' +
      'まちがいの けたが 1つに きまる カードは なおして いんさつします。したの カードは どう ' +
      'なおしても すうじが あわないので、あてずっぽうで つくらず のぞきました。',
    'official.show': 'カードを みる',
    'official.preview': 'シリーズ',
    'official.placeholder': 'シリーズを えらんで「カードを みる」を おしてね。',
    'official.every': 'ぜんぶの シリーズ ({count}まい)',
    'official.option': '{title} ({count}まい)',
    'official.option.one': '{title} (1まい)',
    'official.inJapanese': '{title}',
    'official.everyHint': 'すべての シリーズの カードを じゅんばんに。',
    'footer.local': 'データは この きかいから そとに でません。この ページは、あなたが うごかした サーバーと だけ はなします。',
    'tag.exact': 'ぴったり',
    'tag.closest': 'いちばん ちかい',
    'tag.impossible': 'つくれない',
    'tag.ready': 'できた',
    'tag.working': 'つくっています',
    'tag.done': 'かんりょう',
    'tag.cheat': 'チート',
    'status.exact': 'マシンは この すうじを そのまま よみとります。',
    'status.closest': 'その すうじは この マシンでは つくれません。いちばん ちかい カードです。',
    'status.adjust': 'ここを かえて みてね:',
    'status.again': 'もういちど ためしてね:',
    'status.wrong': 'うまく いきませんでした。ちがう すうじで ためしてね。',
    'status.sheet': '{count}まい、{pages}ページ。',
    'status.sheetOne': '{count}まい、1ページ。',
    'status.drawing': 'カードを かいています...',
    'status.building': 'ファイルを つくっています。おおきい セットは すこし じかんが かかります。',
    'status.saved': 'ダウンロードに ほぞんしました。',
    'status.official': '{count}まい。',
    'status.officialMore':
      '{count}まい。ここでは さいしょの {shown}まいだけ。ダウンロードには ぜんぶ はいっています。',
    'alt.card': '{name} の カード。すうじと バーコードが のっています',
    'alt.page': '{label} {page}ページめ',
    'alt.single': '{label}: いんさつ される とおりの 1まいの カード',
    'label.sheet': 'シート',
    'label.official': 'ほんものの カード',
    wrong: [
      'おしい。マシンは びくとも しない。',
      'ちがうよ。1992ねんに あそんでいた おとなに きいて みたら？',
      'それじゃ ない。マシンが あくびを している。',
    ],
  },
};

function detectLanguage() {
  const browser = navigator.language?.toLowerCase().startsWith('ja') ? 'ja' : 'en';
  try {
    const saved = window.localStorage.getItem(LANGUAGE_KEY);
    return LANGUAGES.includes(saved) ? saved : browser;
  } catch {
    return browser;
  }
}

let currentLanguage = detectLanguage();

function t(key, values = {}) {
  const message = MESSAGES[currentLanguage][key] ?? MESSAGES.en[key] ?? key;
  if (typeof message !== 'string') return message;
  return message.replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ''));
}

function rememberLanguage() {
  try {
    window.localStorage.setItem(LANGUAGE_KEY, currentLanguage);
  } catch {
    document.documentElement.dataset.languageNotRemembered = 'true';
  }
}

function applyLanguage(language) {
  currentLanguage = LANGUAGES.includes(language) ? language : 'en';
  document.documentElement.setAttribute('lang', currentLanguage);
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
    node.setAttribute('placeholder', t(node.dataset.i18nPlaceholder));
  });
  document.querySelectorAll('[data-i18n-aria-label]').forEach((node) => {
    node.setAttribute('aria-label', t(node.dataset.i18nAriaLabel));
  });
  document.querySelectorAll('[data-i18n-alt]').forEach((node) => {
    node.setAttribute('alt', t(node.dataset.i18nAlt));
  });
  document.querySelectorAll('[data-only-language]').forEach((node) => {
    node.toggleAttribute('hidden', node.dataset.onlyLanguage !== currentLanguage);
  });
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === currentLanguage));
  });
  rememberLanguage();
  document.dispatchEvent(new CustomEvent('languagechange', { detail: currentLanguage }));
}
