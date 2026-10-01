import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const URL = process.env.MAEYOMI_URL ?? 'http://127.0.0.1:8000/';
const AXE_URL = 'https://cdn.jsdelivr.net/npm/axe-core@4.13.0/axe.min.js';
const AXE_SHA384 = 'jzJDdyy7z7+/I7TeoAg0Gc8k9hD8b1xRN0W18hMptWJ0cdoiebywhPpCyP9eBOgn';
const RULES = ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'];
const WIDTHS = ['1280', '390'];
const SCHEMES = ['light', 'dark'];
const DEVICES = ['bb2', 'excite94', 'battlerush', 'doraemon3', 'hatayama', 'dslayer2', 'bspace', 'monstmkb', 'kattobi', 'famista3', 'famjock2', 'bardigun', 'cardasobu', 'osharemajo', 'mushiking'];
const TABS = ['one', 'many', 'official', 'shop', 'read', 'cheat'];

const browser = (...args) => execFileSync('agent-browser', args, { encoding: 'utf8' }).trim();
const evaluate = (script) => JSON.parse(JSON.parse(browser('eval', script)));

async function loadAxe() {
  const response = await fetch(AXE_URL);
  if (!response.ok) throw new Error(`axe-core could not be fetched: ${response.status}`);
  const source = await response.text();
  const digest = createHash('sha384').update(source).digest('base64');
  if (digest !== AXE_SHA384) throw new Error(`axe-core does not match its pinned hash: ${digest}`);
  return source;
}

function pickDevice(device) {
  browser('eval', `(() => {
    const toggle = document.getElementById('device-toggle');
    if (toggle.offsetParent !== null && toggle.getAttribute('aria-expanded') === 'false') toggle.click();
    document.querySelector('[data-device="${device}"]').click();
    return 'ok';
  })()`);
  browser('wait', '400');
  const chosen = evaluate(`JSON.stringify(document.querySelector('[aria-current="true"]')?.dataset.device)`);
  if (chosen !== device) throw new Error(`${device} was not chosen: ${chosen}`);
}

function violationsOn(axe, tab) {
  browser('click', `#tab-${tab}`);
  const run = `(async () => {
    const result = await axe.run(document, { runOnly: ${JSON.stringify(RULES)} });
    return JSON.stringify(result.violations.map((found) => [found.id, found.nodes.length]));
  })()`;
  return evaluate(`${axe};\n${run}`);
}

function sweep(axe) {
  const views = [];
  for (const scheme of SCHEMES) {
    browser('set', 'media', scheme);
    for (const width of WIDTHS) {
      browser('set', 'viewport', width, '900');
      for (const device of DEVICES) {
        pickDevice(device);
        for (const tab of TABS) {
          views.push({ scheme, width, device, tab, found: violationsOn(axe, tab) });
        }
      }
    }
  }
  return views;
}

const axe = await loadAxe();
browser('open', URL);
browser('wait', '1500');
const views = sweep(axe);
const bad = views.filter((view) => view.found.length > 0);
bad.forEach((view) => process.stderr.write(`FAIL ${JSON.stringify(view)}\n`));
process.stdout.write(`${views.length} views checked, ${bad.length} with violations\n`);
process.exit(bad.length === 0 ? 0 : 1);
