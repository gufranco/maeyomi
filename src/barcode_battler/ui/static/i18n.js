const LANGUAGES = ['en', 'ja'];
const LANGUAGE_KEY = 'barcode-battler-language';

const MESSAGES = {
  en: {
    title: 'Barcode Battler II card maker',
    lede:
      'Design a fighter, print the sheet, cut the cards, swipe them through the machine. ' +
      'Every card is printed in English and Japanese, with pictures for anyone who cannot read yet.',
    'tabs.label': 'What would you like to make',
    'tab.one': 'One card',
    'tab.many': 'A sheet of cards',
    'tab.official': 'The real cards',
    'cheat.title': 'Cheat activated',
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
    'one.job': 'Type number, 0 to 9',
    'one.job.hint': '0 to 6 is a warrior, 7 to 9 a magician. Some abilities target it.',
    'one.back': 'Make a card the machine reads backwards',
    'one.back.hint': 'Lower limits, and far fewer combinations exist.',
    'one.nearest': 'If those exact numbers are impossible, use the closest ones',
    'one.make': 'Make this card',
    download: 'Download to print',
    'one.preview': 'Your card',
    'one.placeholder': 'Choose your numbers, then press Make this card.',
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
    'official.legend': 'Cards Epoch really sold',
    'official.set': 'Which set',
    'official.note':
      'These are the barcodes printed on the cards Epoch released in Japan, typed in by ' +
      'collectors on the Barcode Battler wiki. The numbers on each card are read from the ' +
      'barcode by this program, not copied from the wiki.',
    'official.skipped': 'Cards left out',
    'official.skipped.hint':
      'The wiki has a typo in these: the last digit does not match the others, so the ' +
      'machine would refuse them. Guessing the right digit would mean printing a card ' +
      'nobody ever sold, so they are left out instead.',
    'official.show': 'Show the cards',
    'official.preview': 'The set',
    'official.placeholder': 'Pick a set and press Show the cards.',
    'official.every': 'Every set, {count} cards',
    'official.option': '{title}, {count} cards',
    'official.inJapanese': 'In Japanese: {title}',
    'official.everyHint': 'Every card from every set, one after another.',
    'cheat.label': 'Secret code',
    'cheat.placeholder': 'psst...',
    'cheat.try': 'Try it',
    'cheat.found': 'Oh no. You found it.',
    printing:
      'Printing: use plain matte paper, turn off any "fit to page" or "scale" setting, and ' +
      'print at the highest quality your printer offers. The barcode only reads at its true size.',
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
    'status.cheat': '{name}: {hp} health, {st} attack, {df} defence, and its attack doubles.',
    'alt.card': 'The card for {name}, showing its numbers and barcode',
    'alt.page': '{label}, page {page}',
    'label.sheet': 'Sheet',
    'label.official': 'Official cards',
    quips: [
      'The machine is sweating.',
      'Please do not tell the other fighters.',
      '99900 health. Your friends will need a bigger calculator.',
      'Attack doubled, because normal attack was just not enough.',
      'Warning: may cause your friends to stop playing with you.',
      'The barcode is real. The fairness is not.',
    ],
    wrong: [
      'Nice try. The machine is not impressed.',
      'Nope. Maybe ask a grown-up who played in 1992?',
      'That is not it. The machine yawns.',
    ],
  },
  ja: {
    title: 'バーコードバトラーII カードメーカー',
    lede:
      'せんしを つくって、いんさつして、きって、マシンに とおそう。' +
      'カードは すべて えいごと にほんごで いんさつされ、もじが よめない こにも わかるように えが つきます。',
    'tabs.label': 'なにを つくる？',
    'tab.one': 'カード 1まい',
    'tab.many': 'カードを まとめて',
    'tab.official': 'ほんものの カード',
    'cheat.title': 'チート はつどう',
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
    'one.job': 'しょくぎょう ばんごう (0〜9)',
    'one.job.hint':
      '0〜6 は せんし、7〜9 は まほうつかい。この ばんごうを ねらう のうりょくも あります。',
    'one.back': 'マシンが うしろから よむ カードに する',
    'one.back.hint': 'つくれる あたいが すくなく なります。',
    'one.nearest': 'その すうじが つくれない ときは、いちばん ちかい カードに する',
    'one.make': 'カードを つくる',
    download: 'いんさつようを ダウンロード',
    'one.preview': 'あなたの カード',
    'one.placeholder': 'すうじを えらんで「カードを つくる」を おしてね。',
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
    'official.legend': 'エポック社が ほんとうに うった カード',
    'official.set': 'どの シリーズ',
    'official.note':
      'エポック社が にほんで はつばいした カードの バーコードを、バーコードバトラー wiki で ' +
      'コレクターが にゅうりょくした ものです。カードの すうじは wiki から うつした ものでは なく、' +
      'この プログラムが バーコードから よみとって います。',
    'official.skipped': 'のぞいた カード',
    'official.skipped.hint':
      'これらは wiki の うちまちがいで、さいごの けたが ほかと あいません。マシンは よみとれません。' +
      'ただしい けたを あてずっぽうで きめると、うられた ことの ない カードに なるので のぞきました。',
    'official.show': 'カードを みる',
    'official.preview': 'シリーズ',
    'official.placeholder': 'シリーズを えらんで「カードを みる」を おしてね。',
    'official.every': 'ぜんぶの シリーズ ({count}まい)',
    'official.option': '{title} ({count}まい)',
    'official.inJapanese': '{title}',
    'official.everyHint': 'すべての シリーズの カードを じゅんばんに。',
    'cheat.label': 'ひみつの コード',
    'cheat.placeholder': 'こっそり...',
    'cheat.try': 'ためす',
    'cheat.found': 'あっ。みつかっちゃった。',
    printing:
      'いんさつ: ふつうの マットな かみを つかい、「ページに あわせる」や「かくだい しゅくしょう」を ' +
      'オフにして、いちばん きれいな がしつで いんさつしてね。バーコードは ほんとうの おおきさで ないと よめません。',
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
    'status.cheat': '{name}: たいりょく {hp}、こうげき {st}、ぼうぎょ {df}、しかも こうげき 2ばい。',
    'alt.card': '{name} の カード。すうじと バーコードが のっています',
    'alt.page': '{label} {page}ページめ',
    'label.sheet': 'シート',
    'label.official': 'ほんものの カード',
    quips: [
      'マシンが あせを かいている。',
      'ほかの せんしには ないしょだよ。',
      'たいりょく 99900。ともだちは おおきな でんたくが ひつようかも。',
      'こうげき 2ばい。ふつうの こうげきでは たりなかったから。',
      'ちゅうい: ともだちが あそんで くれなく なるかも。',
      'バーコードは ほんもの。フェアさは ない。',
    ],
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
  document.querySelectorAll('[data-only-language]').forEach((node) => {
    node.toggleAttribute('hidden', node.dataset.onlyLanguage !== currentLanguage);
  });
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === currentLanguage));
  });
  rememberLanguage();
  document.dispatchEvent(new CustomEvent('languagechange', { detail: currentLanguage }));
}
