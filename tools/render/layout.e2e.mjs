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

function checkNotes() {
  browser('click', '#tab-official');
  const notes = evaluate(`JSON.stringify({
    details: document.querySelectorAll('details').length,
    links: [...document.querySelectorAll('#official-note a')].map((link) => link.href),
    skipped: getComputedStyle(document.getElementById('official-rejected')).display,
  })`);
  expect(notes.details === 0, `${notes.details} explanations hide behind a click`);
  expect(notes.links.some((link) => link.includes('wikiwiki.jp')), 'the wiki is not linked');
  expect(notes.links.some((link) => link.includes('puNES')), 'puNES is not linked');
  expect(notes.skipped !== 'none', 'the cards left out are not visible');
}

browser('open', URL);
browser('wait', '1500');
checkWidths();
checkDeviceSwitch();
checkNotes();
failures.forEach((failure) => process.stderr.write(`FAIL ${failure}\n`));
process.stdout.write(failures.length ? '' : 'layout checks passed\n');
process.exit(failures.length ? 1 : 0);
