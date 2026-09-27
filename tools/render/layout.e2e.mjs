import { execFileSync } from 'node:child_process';

const URL = process.env.MAEYOMI_URL ?? 'http://127.0.0.1:8000/';
const TABS = ['one', 'many', 'official', 'shop', 'read'];
const WIDTHS = [320, 1280];
const failures = [];

const browser = (...args) => execFileSync('agent-browser', args, { encoding: 'utf8' }).trim();

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

function checkDeviceMenu() {
  const menu = evaluate(`JSON.stringify([...document.querySelectorAll('#device optgroup')]
    .map((group) => [group.label, [...group.querySelectorAll('option')].map((o) => o.text)]))`);
  expect(menu.length === 2 && menu[0][0] === 'Machines' && menu[1][0] === 'Games',
    `the device menu is grouped as ${JSON.stringify(menu)}`);
  const machines = menu[0]?.[1] ?? [];
  const sorted = machines.toSorted((first, second) => first.localeCompare(second, 'en'));
  expect(JSON.stringify(machines) === JSON.stringify(sorted), `machines are ordered ${machines}`);
  expect(!machines.some((name) => /\bII\b|²/.test(name)), `a machine name is ${machines}`);
}

function checkJobMenu() {
  browser('select', '#device', 'double');
  const double = evaluate(`JSON.stringify([...document.querySelectorAll('#job option')].map((o) => o.text))`);
  expect(double.length === 11 && double[5] === '4: Priest' && double[7] === '6: Holy warrior',
    `the Double's types are ${double}`);
  browser('select', '#device', 'bb2');
  const second = evaluate(`JSON.stringify([...document.querySelectorAll('#job option')].map((o) => o.text))`);
  expect(second[8] === '7: Magician', `the II's types are ${second}`);
}

function checkBackRead() {
  browser('select', '#device', 'bb2');
  browser('click', '#tab-one');
  browser('check', '#backRead');
  const back = evaluate(`JSON.stringify(['hp', 'st', 'df'].map((key) =>
    [document.getElementById(key).min, document.getElementById(key).max]))`);
  expect(JSON.stringify(back) === JSON.stringify([['0', '49900'], ['2000', '11900'], ['0', '9900']]),
    `a backwards II card offers ${JSON.stringify(back)}`);
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
  browser('select', '#device', 'dbz');
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
  browser('select', '#device', 'bb2');
}

function realCards(device) {
  browser('select', '#device', device);
  browser('click', '#tab-official');
  browser('wait', '800');
  return evaluate(`JSON.stringify({
    details: document.querySelectorAll('details').length,
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
  expect(second.skipped, 'the II hides the cards left out');
  const dbz = realCards('dbz');
  expect(!dbz.picker, 'Dragon Ball Z has one set yet shows a set picker');
  expect(dbz.single.includes('36'), `Dragon Ball Z names its set as ${dbz.single}`);
  expect(dbz.links.length === 1 && dbz.links[0].includes('puNES'),
    `Dragon Ball Z's real cards link ${dbz.links}`);
  expect(!dbz.skipped, 'Dragon Ball Z shows an empty list of cards left out');
  browser('select', '#device', 'bb2');
}

function checkSheetAndShop() {
  browser('select', '#device', 'dbz');
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
  browser('select', '#device', 'bb2');
}

browser('open', URL);
browser('wait', '1500');
checkDeviceMenu();
checkJobMenu();
checkBackRead();
checkWidths();
checkDeviceSwitch();
checkRealCards();
checkSheetAndShop();
failures.forEach((failure) => process.stderr.write(`FAIL ${failure}\n`));
process.stdout.write(failures.length ? '' : 'layout checks passed\n');
process.exit(failures.length ? 1 : 0);
