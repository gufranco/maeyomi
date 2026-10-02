import { execFileSync } from 'node:child_process';

const URL = process.env.MAEYOMI_URL ?? 'http://127.0.0.1:8000/';
const TABS = ['one', 'many', 'official', 'shop', 'read', 'cheat'];
const WIDTHS = [320, 1280];
const failures = [];

const browser = (...args) => execFileSync('agent-browser', args, { encoding: 'utf8' }).trim();

const pickDevice = (key) => {
  browser('eval', `(() => {
    const toggle = document.getElementById('device-toggle');
    if (toggle.offsetParent !== null && toggle.getAttribute('aria-expanded') === 'false') toggle.click();
    document.querySelector('[data-device="${key}"]').scrollIntoView({ block: 'center' });
    return 'ok';
  })()`);
  browser('click', `[data-device="${key}"]`);
};

const evaluate = (script) => JSON.parse(JSON.parse(browser('eval', script)));

function expect(condition, message) {
  if (!condition) failures.push(message);
}

function checkWidths() {
  WIDTHS.forEach((width) => {
    browser('set', 'viewport', String(width), '900');
    TABS.forEach((tab) => {
      browser('click', `#tab-${tab}`);
      const page = evaluate('JSON.stringify(document.documentElement.scrollWidth)');
      expect(page <= width, `${tab} at ${width}px scrolls sideways: ${page}px wide`);
    });
  });
}

function checkInlineCheckboxes() {
  browser('set', 'viewport', '390', '844');
  browser('click', '#tab-one');
  const rows = evaluate(`JSON.stringify([...document.querySelectorAll('.field.check label')]
    .filter((label) => label.offsetParent !== null)
    .map((label) => {
      const box = label.querySelector('input').getBoundingClientRect();
      const text = label.querySelector('span').getBoundingClientRect();
      return Math.abs((box.top + box.bottom) / 2 - (text.top + text.bottom) / 2) < text.height;
    }))`);
  expect(rows.length > 0 && rows.every(Boolean), `a checkbox sits apart from its text: ${rows}`);
  browser('set', 'viewport', '1280', '900');
}

function checkDeviceMenu() {
  const menu = evaluate(`JSON.stringify([...document.querySelectorAll('#device .list-heading')]
    .map((heading) => [heading.textContent, [...heading.nextElementSibling.querySelectorAll('.item-name')]
      .map((name) => name.textContent)]))`);
  const headings = menu.map(([heading]) => heading);
  expect(JSON.stringify(headings) === JSON.stringify([
    'Machines',
    'Super Famicom, through the Barcode Battler II',
    'Famicom Datach',
    'Famicom, through the Barcode Battler II',
    'Game Boy',
    'Nintendo DS',
    'Advanced Pico Beena',
  ]), `the device list is grouped as ${JSON.stringify(headings)}`);
  const machines = menu[0]?.[1] ?? [];
  const sorted = machines.toSorted((first, second) => first.localeCompare(second, 'en'));
  expect(JSON.stringify(machines) === JSON.stringify(sorted), `machines are ordered ${machines}`);
  expect(!machines.some((name) => /\bII\b|²/.test(name)), `a machine name is ${machines}`);
  pickDevice('dbz');
  const current = evaluate(`JSON.stringify(document.querySelector('[aria-current="true"]')?.dataset.device)`);
  expect(current === 'dbz', `the chosen device is not marked current: ${current}`);
  pickDevice('bb2');
}

function checkJobMenu() {
  pickDevice('double');
  const double = evaluate(`JSON.stringify([...document.querySelectorAll('#job option')].map((o) => o.text))`);
  expect(double.length === 11 && double[5] === '4: Priest' && double[7] === '6: Holy warrior',
    `the Double's types are ${double}`);
  pickDevice('bb2');
  const second = evaluate(`JSON.stringify([...document.querySelectorAll('#job option')].map((o) => o.text))`);
  expect(second[8] === '7: Magician', `the II's types are ${second}`);
}

function checkBackRead() {
  pickDevice('bb2');
  browser('click', '#tab-one');
  browser('check', '#backRead');
  const back = evaluate(`JSON.stringify(['hp', 'st', 'df'].map((key) =>
    [document.getElementById(key).min, document.getElementById(key).max]))`);
  expect(JSON.stringify(back) === JSON.stringify([['0', '49900'], ['2000', '11900'], ['0', '9900']]),
    `a backwards II card offers ${JSON.stringify(back)}`);
  const boxes = evaluate(`JSON.stringify(['hp', 'st', 'df'].map((key) =>
    document.getElementById(key + '-box').value === document.getElementById(key).value))`);
  expect(boxes.every(Boolean), `a number box disagrees with its slider: ${boxes}`);
  browser('fill', '#hp-box', '60000');
  browser('press', 'Tab');
  const tooHigh = evaluate(`JSON.stringify(document.getElementById('hp-box-problem')?.textContent)`);
  expect(tooHigh === 'Use a number from 0 to 49900.', `typing 60000 backwards says ${tooHigh}`);
  browser('fill', '#hp-box', '30000');
  browser('press', 'Tab');
  const typed = evaluate(`document.getElementById('hp').value`);
  expect(typed === 30000, `typing 30000 moves the slider to ${typed}`);
  browser('uncheck', '#backRead');
  const front = evaluate(`document.getElementById('hp').max`);
  expect(front === 99900, `a front-read II card stops health at ${front}`);
  const order = evaluate(`JSON.stringify([...document.querySelectorAll('#one .field:not([hidden]) label')]
    .map((label) => label.getAttribute('for')))`);
  expect(order.indexOf('backRead') === order.indexOf('race') + 1,
    `reading backwards does not follow the kind of fighter: ${order}`);
}

function checkDeviceSwitch() {
  browser('click', '#tab-one');
  pickDevice('dbz');
  const form = evaluate(`JSON.stringify({
    race: getComputedStyle(document.querySelector('[data-device-field=race]')).display,
    dbz: getComputedStyle(document.querySelector('[data-device-field=dbz]')).display,
    bp: document.querySelector('label[for=st]').textContent,
    hpStep: document.getElementById('hp').step,
  })`);
  expect(form.race === 'none', `the race field shows for Dragon Ball Z: ${form.race}`);
  expect(form.dbz !== 'none', 'the Dragon Ball Z fighter field is hidden');
  expect(form.bp === 'Battle power', `the attack slider is labelled ${form.bp}`);
  expect(form.hpStep === '500', `the health slider steps by ${form.hpStep}`);
  pickDevice('ultraman');
  browser('wait', '600');
  const game = evaluate(`JSON.stringify({
    picker: getComputedStyle(document.querySelector('[data-device-field=game]')).display,
    cards: document.querySelectorAll('#game-character option[value]:not([value=""])').length,
    dbz: getComputedStyle(document.querySelector('[data-device-field=dbz]')).display,
    power: document.querySelector('label[for=hp]').textContent,
    hpMax: document.getElementById('hp').max,
  })`);
  expect(game.picker !== 'none', 'the Ultraman Club card picker is hidden');
  expect(game.cards === 51, `the Ultraman Club picker lists ${game.cards} cards`);
  expect(game.dbz === 'none', 'the Dragon Ball Z field shows for Ultraman Club');
  expect(game.power === 'PW', `the first Ultraman Club slider is labelled ${game.power}`);
  expect(game.hpMax === '9900', `the PW slider stops at ${game.hpMax}`);
  pickDevice('sdgundam');
  browser('wait', '600');
  evaluate(`(() => { const select = document.getElementById('game-character');
    select.value = '0'; select.dispatchEvent(new Event('change')); return JSON.stringify(true); })()`);
  browser('wait', '600');
  const unit = evaluate(`JSON.stringify({
    picks: [...document.querySelectorAll('#game-picks select')].map((select) => select.id),
    shown: document.getElementById('game-picks').offsetParent !== null,
  })`);
  expect(unit.shown, 'the SD Gundam unit choices are hidden');
  expect(unit.picks.join() === 'pick-sr,pick-lr,pick-cp',
    `the SD Gundam unit offers ${unit.picks}`);
  pickDevice('yuyu');
  browser('wait', '600');
  evaluate(`(() => { const select = document.getElementById('game-character');
    select.value = '0'; select.dispatchEvent(new Event('change')); return JSON.stringify(true); })()`);
  browser('wait', '600');
  const fighter = evaluate(`JSON.stringify({
    sliders: document.getElementById('hp').offsetParent !== null,
    picks: [...document.querySelectorAll('#game-picks select')].map((select) => select.id),
    options: document.querySelectorAll('#pick-moves option').length,
  })`);
  expect(!fighter.sliders, 'Yu Yu Hakusho shows number sliders no barcode changes');
  expect(fighter.picks.join() === 'pick-moves', `the Yu Yu Hakusho fighter offers ${fighter.picks}`);
  expect(fighter.options > 2, `Yusuke offers ${fighter.options} technique choices`);
  pickDevice('jleague');
  browser('wait', '600');
  const league = evaluate(`JSON.stringify({
    sliders: document.getElementById('hp').offsetParent !== null,
    cards: document.querySelectorAll('#game-character option[value]:not([value=""])').length,
  })`);
  expect(!league.sliders, 'J.League shows number sliders its cards do not carry');
  expect(league.cards === 160, `the J.League picker lists ${league.cards} cards`);
  pickDevice('barcodeworld');
  browser('wait', '600');
  evaluate(`(() => { const select = document.getElementById('game-character');
    select.value = '1'; select.dispatchEvent(new Event('change')); return JSON.stringify(true); })()`);
  browser('wait', '600');
  const world = evaluate(`JSON.stringify({
    hpMax: document.getElementById('hp').max,
    jobs: [...document.querySelectorAll('#pick-job option')].map((option) => option.value).join(),
  })`);
  expect(world.hpMax === '49900', `the Barcode World health slider stops at ${world.hpMax}`);
  expect(world.jobs === ',7,8,9', `a Barcode World magician offers jobs ${world.jobs}`);
  pickDevice('senki');
  browser('wait', '600');
  const senki = evaluate(`JSON.stringify({ hpMax: document.getElementById('hp').max })`);
  expect(senki.hpMax === '49900', `the Senki health slider stops at ${senki.hpMax}`);
  pickDevice('lupin');
  browser('wait', '600');
  const lupin = evaluate(`JSON.stringify({
    sliders: document.getElementById('hp').offsetParent !== null,
    effects: document.querySelectorAll('#game-character option[value]:not([value=""])').length,
  })`);
  expect(!lupin.sliders, 'Lupin III shows number sliders its codes do not carry');
  expect(lupin.effects === 11, `the Lupin III picker lists ${lupin.effects} effects`);
  pickDevice('bb2');
}

function realCards(device) {
  pickDevice(device);
  browser('click', '#tab-official');
  browser('wait', '800');
  return evaluate(`JSON.stringify({
    details: document.querySelectorAll('#panel-official details').length,
    links: [...document.querySelectorAll('#official-note a')]
      .filter((link) => link.offsetParent !== null).map((link) => link.href),
    picker: document.getElementById('official-set-field').offsetParent !== null,
    single: document.getElementById('official-single').textContent,
    skipped: document.getElementById('official-skipped').offsetParent !== null,
  })`);
}

function checkRealCards() {
  const second = realCards('bb2');
  expect(second.details === 0, `${second.details} explanations hide behind a click`);
  expect(second.picker, 'the II has nine sets but no set picker');
  expect(second.links.length === 1 && second.links[0].includes('wikiwiki.jp'),
    `the II's real cards link ${second.links}`);
  expect(!second.skipped, 'the II shows an empty list of cards left out');
  const dbz = realCards('dbz');
  expect(!dbz.picker, 'Dragon Ball Z has one set yet shows a set picker');
  expect(dbz.single.includes('36'), `Dragon Ball Z names its set as ${dbz.single}`);
  expect(dbz.links.length === 1 && dbz.links[0].includes('puNES'),
    `Dragon Ball Z's real cards link ${dbz.links}`);
  expect(!dbz.skipped, 'Dragon Ball Z shows an empty list of cards left out');
  const ultraman = realCards('ultraman');
  expect(ultraman.single.includes('38'), `Ultraman Club names its set as ${ultraman.single}`);
  expect(ultraman.links.length === 1 && ultraman.links[0].includes('retrostuff.org'),
    `Ultraman Club's real cards link ${ultraman.links}`);
  const gundam = realCards('sdgundam');
  expect(gundam.single.includes('76'), `SD Gundam Wars names its set as ${gundam.single}`);
  expect(gundam.links.length === 1 && gundam.links[0].includes('sd-gundam'),
    `SD Gundam Wars's real cards link ${gundam.links}`);
  const yuyu = realCards('yuyu');
  expect(yuyu.single.includes('37'), `Yu Yu Hakusho names its set as ${yuyu.single}`);
  expect(yuyu.links.length === 1 && yuyu.links[0].includes('archive.org'),
    `Yu Yu Hakusho's real cards link ${yuyu.links}`);
  const league = realCards('jleague');
  expect(league.single.includes('160'), `J.League names its set as ${league.single}`);
  expect(league.links.length === 1 && league.links[0].includes('j-league'),
    `J.League's real cards link ${league.links}`);
  const world = realCards('barcodeworld');
  expect(world.single.includes('24'), `Barcode World names its set as ${world.single}`);
  expect(world.links.length === 1 && world.links[0].includes('BarcodeWorld'),
    `Barcode World's real cards link ${world.links}`);
  const senki = realCards('senki');
  const senkiForm = evaluate(`JSON.stringify({
    actions: document.getElementById('official-actions').offsetParent !== null,
    note: document.querySelector('[data-official-source="senki"]').offsetParent !== null,
  })`);
  expect(!senki.picker && !senkiForm.actions, 'Senki offers to print a set it does not have');
  expect(senkiForm.note, 'Senki does not say why it has no real cards');
  expect(senki.links.length === 1 && senki.links[0].includes('wikipedia'),
    `Senki's real cards link ${senki.links}`);
  const alice = realCards('alice');
  const aliceForm = evaluate(`JSON.stringify({
    actions: document.getElementById('official-actions').offsetParent !== null,
    sources: document.getElementById('official-sources').offsetParent !== null,
  })`);
  expect(!alice.picker && !aliceForm.actions, 'Alice offers to print a set it does not have');
  expect(aliceForm.sources && alice.links.length === 1 && alice.links[0].includes('setsumei'),
    `Alice does not link the manual that shows it had no cards: ${alice.links}`);
  pickDevice('bb2');
}

function checkSheetAndShop() {
  pickDevice('dbz');
  browser('click', '#tab-many');
  const sheet = evaluate(`JSON.stringify({
    race: document.querySelector('[data-sheet-field=race]').offsetParent !== null,
    hpMin: document.getElementById('hp-min').value,
    label: document.querySelector('label[for=st-min]').textContent,
  })`);
  expect(!sheet.race, 'the sheet offers a race for Dragon Ball Z');
  expect(sheet.hpMin === '10000', `the Dragon Ball Z sheet starts at ${sheet.hpMin} health`);
  expect(sheet.label === 'Battle power', `the sheet labels attack as ${sheet.label}`);
  browser('click', '#tab-shop');
  browser('click', '#shop-surprise');
  browser('wait', '2500');
  const shop = evaluate(`JSON.stringify({
    rows: [...document.querySelectorAll('.shelf-stats')].map((row) => row.textContent),
  })`);
  expect(shop.rows.length === 9, `the surprise shelf has ${shop.rows.length} products`);
  expect(!shop.rows.some((row) => row.includes('ST ')), 'the shelf shows II numbers for DBZ');
  pickDevice('bb2');
}

function checkBehaviour() {
  browser('click', '#tab-many');
  browser('fill', '#count', '500');
  const problem = evaluate(`JSON.stringify(document.getElementById('count-problem')?.textContent)`);
  expect(problem === 'Use a number from 1 to 200.', `an out-of-range count says ${problem}`);
  browser('fill', '#count', '9');
  const hash = evaluate('JSON.stringify(window.location.hash)');
  expect(hash === '#tab=many', `the address does not name the open tab: ${hash}`);
  browser('open', URL.replace(/#.*$/, '') + '#official');
  browser('wait', '1500');
  const open = evaluate(`JSON.stringify(document.getElementById('tab-official').getAttribute('aria-selected'))`);
  expect(open === 'true', 'a link to #official does not open that tab');
}

function checkFreshStartOnDeviceChange() {
  browser('click', '#tab-one');
  browser('click', '#one button[type=submit]');
  browser('wait', '--fn', "document.getElementById('card-image').hasAttribute('src')");
  const made = evaluate(`JSON.stringify(document.getElementById('card-image').hasAttribute('src'))`);
  browser('click', '#tab-many');
  pickDevice('bb1');
  const after = evaluate(`JSON.stringify([
    document.getElementById('tab-one').getAttribute('aria-selected'),
    document.getElementById('card-image').hasAttribute('src'),
    document.getElementById('card-placeholder').hidden,
    document.getElementById('one-status').textContent.trim(),
  ])`);
  expect(made, 'the one-card tab never showed a card to clear');
  expect(after[0] === 'true' && !after[1] && !after[2] && after[3] === '',
    `choosing a device does not return to a clean One card tab: ${after}`);
  pickDevice('bb2');
}

function checkLivePreview() {
  browser('click', '#tab-one');
  browser('wait', '1500');
  const before = evaluate(`JSON.stringify(document.getElementById('one-code-value').textContent)`);
  browser('eval', `(() => {
    const box = document.getElementById('hp-box');
    box.value = '7000';
    box.dispatchEvent(new Event('change', { bubbles: true }));
    return 'ok';
  })()`);
  browser('wait', '2000');
  const after = evaluate(`JSON.stringify([
    document.getElementById('one-code-value').textContent,
    document.getElementById('card-image').hasAttribute('src'),
  ])`);
  expect(before !== '' && after[1] && after[0] !== before,
    `the card does not redraw as the numbers change: ${before} then ${after}`);
}

function checkFoldedOptions() {
  const folded = evaluate(`JSON.stringify([
    document.getElementById('one-more').open,
    !document.getElementById('ability').checkVisibility({ contentVisibilityAuto: true }),
  ])`);
  expect(!folded[0] && folded[1], `the extra options are not folded away: ${folded}`);
}

function checkAddressAndKeys() {
  pickDevice('dbz');
  const address = evaluate('JSON.stringify(window.location.search)');
  expect(address === '?device=dbz', `the address does not name the device: ${address}`);
  browser('press', 'Escape');
  browser('eval', "document.activeElement.blur(); 'ok'");
  browser('press', '/');
  const focused = evaluate('JSON.stringify(document.activeElement.id)');
  expect(focused === 'device-filter', `the slash key focuses ${focused}`);
  browser('fill', '#device-filter', 'ultraman');
  browser('press', 'Enter');
  browser('wait', '600');
  const chosen = evaluate(`JSON.stringify(document.querySelector('[aria-current="true"]')?.dataset.device)`);
  expect(chosen === 'ultraman', `Enter in the filter chose ${chosen}`);
  browser('eval', "history.back(); 'ok'");
  browser('wait', '800');
  const back = evaluate(`JSON.stringify(document.querySelector('[aria-current="true"]')?.dataset.device)`);
  expect(back === 'dbz', `going back returns to ${back}`);
  pickDevice('bb2');
}

function checkEmptyRealCards() {
  pickDevice('lupin');
  browser('click', '#tab-official');
  browser('wait', '800');
  const empty = evaluate(`JSON.stringify([
    document.getElementById('official-sets').offsetParent === null,
    document.getElementById('official-preview').offsetParent === null,
    document.getElementById('official-note').offsetParent !== null,
  ])`);
  expect(empty.every(Boolean), `a game with no cards still shows empty parts: ${empty}`);
  pickDevice('dslayer2');
  browser('click', '#tab-official');
  browser('wait', '800');
  const selios = evaluate(`JSON.stringify([
    document.getElementById('official-actions').offsetParent !== null,
    document.getElementById('official-single').textContent,
  ])`);
  expect(selios[0] && selios[1].includes('1'), `Dragon Slayer II does not offer the Selios card: ${selios}`);
  pickDevice('bb2');
}

function checkPhoneTabsFit() {
  browser('set', 'viewport', '390', '844');
  const hidden = evaluate(`JSON.stringify([...document.querySelectorAll('[role="tab"]')]
    .filter((tab) => { const box = tab.getBoundingClientRect(); return box.right > innerWidth || box.left < 0; })
    .map((tab) => tab.id))`);
  expect(hidden.length === 0, `tabs off screen on a phone: ${hidden}`);
  browser('set', 'viewport', '1280', '900');
}

function checkCheatLinkShowsThatDevicesCard() {
  browser('open', `${URL.replace(/#.*$/, '')}?device=battlerush#tab-cheat`);
  browser('wait', '3000');
  const pair = evaluate(`(async () => {
    const response = await fetch('/api/cheat-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device: 'battlerush', kind: 'all' }),
    });
    const expected = (await response.json()).pages.length;
    return JSON.stringify([document.querySelectorAll('#cheat-frame img').length, expected]);
  })()`);
  expect(pair[0] === pair[1] && pair[0] > 0, `a link to the cheat tab shows another device's cards: ${pair}`);
  browser('open', URL.replace(/#.*$/, ''));
  browser('wait', '1500');
  browser('set', 'viewport', '1280', '900');
  pickDevice('bb2');
}

function checkCheatKindsFollowThePickAndTheLanguage() {
  browser('open', `${URL.replace(/#.*$/, '')}?device=famista3#tab-cheat`);
  browser('wait', '3000');
  const state = evaluate(`(async () => {
    const select = document.getElementById('cheat-kind');
    const keys = [...select.options].map((option) => option.value);
    select.value = 'era';
    select.dispatchEvent(new Event('change'));
    await new Promise((done) => setTimeout(done, 2500));
    const response = await fetch('/api/device-cheat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device: 'famista3', kind: 'era' }),
    });
    const expected = (await response.json()).barcode;
    document.querySelector('[data-language="ja"]').click();
    await new Promise((done) => setTimeout(done, 800));
    const japanese = select.selectedOptions[0].text;
    document.querySelector('[data-language="en"]').click();
    return JSON.stringify([keys.join(','), document.getElementById('cheat-code-value').textContent, expected, japanese]);
  })()`);
  expect(state[0] === 'all,strongest,average,speed,era,pitch,stamina', `Famista 3 offers other cheat kinds: ${state[0]}`);
  expect(state[1] === state[2], `picking a cheat kind shows another card: ${state}`);
  expect(/[\u3040-\u30ff]/.test(state[3]), `a cheat kind stays in English on the Japanese page: ${state[3]}`);
  browser('open', URL.replace(/#.*$/, ''));
  browser('wait', '1500');
  pickDevice('bb2');
}

function checkNothingIsFocusedOnOpen() {
  for (const [address, tab] of [['', 'tab-one'], ['#tab=many', 'tab-many'], ['#tab-cheat', 'tab-cheat']]) {
    browser('open', 'about:blank');
    browser('open', `${URL}${address}`);
    browser('wait', '1500');
    const state = evaluate(`JSON.stringify([
      document.activeElement === document.body,
      document.querySelector('[role="tab"][aria-selected="true"]').id,
    ])`);
    expect(state[0] && state[1] === tab, `opening ${address || 'the page'} focuses something or opens the wrong tab: ${state}`);
  }
  browser('click', '#tab-one');
}

function checkLanguageLeavesTheCard() {
  browser('click', '#tab-one');
  browser('wait', '1500');
  const card = () => evaluate(`JSON.stringify(document.getElementById('card-image').getAttribute('src'))`);
  const before = card();
  browser('eval', `document.querySelector('[data-language="ja"]').click(); 'ok'`);
  browser('wait', '1500');
  const lang = evaluate(`JSON.stringify(document.documentElement.lang)`);
  expect(lang === 'ja' && card() === before, `switching the page to Japanese changed the card: ${lang}`);
  browser('eval', `document.querySelector('[data-language="en"]').click(); 'ok'`);
  browser('wait', '1000');
}

function checkCheatTab() {
  browser('click', '#tab-cheat');
  browser('wait', '2000');
  const shown = evaluate(`JSON.stringify([
    document.querySelectorAll('#cheat-frame img').length,
    document.getElementById('cheat-kind').value,
    document.getElementById('tab-cheat').textContent.trim(),
  ])`);
  expect(shown[0] > 0 && shown[1] === 'all' && shown[2] === 'Cheats', `the cheat tab shows no sheet of every kind: ${shown}`);
  pickDevice('dbz');
  const after = evaluate(`JSON.stringify([
    document.getElementById('tab-one').getAttribute('aria-selected'),
    document.querySelectorAll('#cheat-frame img').length > 0,
  ])`);
  expect(after[0] === 'true' && !after[1], `changing device leaves the cheat card: ${after}`);
  pickDevice('bb2');
}

function checkOneCheatCardStandsAlone() {
  pickDevice('bardigun');
  browser('click', '#tab-cheat');
  browser('wait', '2500');
  const together = evaluate(`JSON.stringify([
    document.getElementById('cheat-frame').classList.contains('single'),
    document.getElementById('cheat-name-field').hidden,
    document.getElementById('cheat-name-all').hidden,
  ])`);
  expect(!together[0] && together[1] && !together[2], `every kind together is not a named sheet: ${together}`);
  browser('select', '#cheat-kind', 'power');
  browser('wait', '2500');
  const alone = evaluate(`JSON.stringify([
    document.getElementById('cheat-frame').classList.contains('single'),
    document.querySelectorAll('#cheat-frame img').length,
    document.getElementById('cheat-name-field').hidden,
    document.getElementById('cheat-name').placeholder,
  ])`);
  expect(alone[0] && alone[1] === 1 && !alone[2] && alone[3] === 'Most power', `one cheat card is not shown alone: ${alone}`);
  pickDevice('bb2');
}

function checkOneCardSheetStandsAlone() {
  browser('click', '#tab-many');
  browser('wait', '800');
  browser('eval', "document.getElementById('count').value = '1'; document.getElementById('many').requestSubmit(); 'ok'");
  browser('wait', '3000');
  const shown = evaluate(`JSON.stringify([
    document.getElementById('sheet-frame').classList.contains('single'),
    document.querySelectorAll('#sheet-frame img').length,
  ])`);
  expect(shown[0] && shown[1] === 1, `a one-card sheet is not shown alone: ${shown}`);
  browser('eval', "document.getElementById('count').value = '9'; 'ok'");
  browser('click', '#tab-one');
}

function checkCode39ReadTab() {
  pickDevice('cardasobu');
  browser('click', '#tab-read');
  browser('wait', '800');
  browser('fill', '#read-barcode', '*aa082krc00v01*');
  browser('eval', "document.getElementById('read').requestSubmit(); 'ok'");
  browser('wait', '2500');
  const read = evaluate(`JSON.stringify([
    document.getElementById('read-barcode').getAttribute('inputmode'),
    document.getElementById('read-status').textContent.includes('This is what the machine sees'),
    document.getElementById('read-facts').textContent.includes('Whale'),
  ])`);
  expect(read[0] === 'text' && read[1] && read[2], `a Code 39 card is not read on the Read tab: ${read}`);
  browser('click', '#tab-one');
  pickDevice('bb2');
}

function checkPhoneDeviceMenu() {
  browser('set', 'viewport', '390', '844');
  const closed = evaluate(`JSON.stringify([
    document.getElementById('device-toggle').offsetParent !== null,
    document.getElementById('device').offsetParent === null,
  ])`);
  expect(closed[0] && closed[1], `the phone device menu does not start closed: ${closed}`);
  pickDevice('dbz');
  const after = evaluate(`JSON.stringify([
    document.getElementById('device-toggle').getAttribute('aria-expanded'),
    document.getElementById('device-current').textContent,
  ])`);
  expect(after[0] === 'false' && after[1] === 'Datach Dragon Ball Z',
    `choosing on a phone does not close the menu and name the choice: ${after}`);
  pickDevice('bb2');
  browser('set', 'viewport', '1280', '900');
}

const deviceListScrolls = () => evaluate(`JSON.stringify(['sidebar', 'device-panel', 'device']
  .map((id) => document.getElementById(id))
  .filter((node) => node.offsetParent !== null)
  .some((node) => node.scrollHeight > node.clientHeight + 1
    || ['auto', 'scroll'].includes(getComputedStyle(node).overflowY)))`);

function checkDeviceListNeverScrolls() {
  expect(!deviceListScrolls(), 'the machine or game list has a scroll bar on a wide screen');
  browser('set', 'viewport', '390', '844');
  browser('click', '#device-toggle');
  expect(!deviceListScrolls(), 'the machine or game list has a scroll bar on a phone');
  browser('click', '#device-toggle');
  browser('set', 'viewport', '1280', '900');
}

function checkDeviceFilter() {
  browser('fill', '#device-filter', 'datach');
  const shown = evaluate(`JSON.stringify([...document.querySelectorAll('#device [data-device]')]
    .filter((button) => !button.closest('li').hidden).map((button) => button.dataset.device))`);
  expect(shown.length === 6 && shown.every((key) => key !== 'bb2'),
    `the filter for datach shows ${shown}`);
  browser('fill', '#device-filter', '');
}

browser('open', URL);
browser('wait', '1500');
browser('set', 'viewport', '1280', '900');
pickDevice('bb2');
checkDeviceMenu();
checkDeviceFilter();
checkDeviceListNeverScrolls();
checkLivePreview();
checkFoldedOptions();
checkFreshStartOnDeviceChange();
checkAddressAndKeys();
checkEmptyRealCards();
checkNothingIsFocusedOnOpen();
checkLanguageLeavesTheCard();
checkCheatTab();
checkOneCheatCardStandsAlone();
checkOneCardSheetStandsAlone();
checkCode39ReadTab();
checkCheatLinkShowsThatDevicesCard();
checkCheatKindsFollowThePickAndTheLanguage();
checkPhoneTabsFit();
checkPhoneDeviceMenu();
checkInlineCheckboxes();
checkJobMenu();
checkBackRead();
checkWidths();
checkDeviceSwitch();
checkRealCards();
checkSheetAndShop();
checkBehaviour();
failures.forEach((failure) => process.stderr.write(`FAIL ${failure}\n`));
process.stdout.write(failures.length ? '' : 'layout checks passed\n');
process.exit(failures.length ? 1 : 0);
