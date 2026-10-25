import AxeBuilder from '@axe-core/playwright';
import { chromium } from 'playwright';

const URL = process.env.MAEYOMI_URL ?? 'http://127.0.0.1:8000/';
const RULES = ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'];
const WIDTHS = [1280, 390];
const SCHEMES = ['light', 'dark'];
const DEFAULT_DEVICES = ['bb2', 'excite94', 'battlerush', 'doraemon3', 'hatayama', 'dslayer2', 'bspace', 'monstmkb', 'kattobi', 'famista3', 'famjock2', 'bardigun', 'cardasobu', 'osharemajo', 'mushiking', 'wantame', 'rockman', 'densha', 'anpanman', 'ochaken'];
const DEVICES = (process.env.MAEYOMI_A11Y_DEVICES ?? DEFAULT_DEVICES.join(',')).split(',').filter(Boolean);
const TABS = ['one', 'many', 'official', 'shop', 'read', 'cheat'];

async function pickDevice(page, device) {
  await page.waitForSelector(`[data-device="${device}"]`, { state: 'attached' });
  await page.evaluate((wanted) => {
    const toggle = document.getElementById('device-toggle');
    if (toggle && toggle.offsetParent !== null && toggle.getAttribute('aria-expanded') === 'false') {
      toggle.click();
    }
    document.querySelector(`[data-device="${wanted}"]`).click();
  }, device);
  await page.waitForTimeout(400);
  const chosen = await page.evaluate(() => document.querySelector('[aria-current="true"]')?.dataset.device);
  if (chosen !== device) {
    throw new Error(`${device} was not chosen: ${chosen}`);
  }
}

async function violationsOn(page, tab) {
  await page.waitForSelector(`#tab-${tab}`);
  await page.click(`#tab-${tab}`);
  const result = await new AxeBuilder({ page }).withTags(RULES).analyze();
  return result.violations.map((found) => [found.id, found.nodes.length]);
}

const browser = await chromium.launch();
const views = [];
for (const scheme of SCHEMES) {
  const context = await browser.newContext({ colorScheme: scheme });
  const page = await context.newPage();
  for (const width of WIDTHS) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(URL, { waitUntil: 'load' });
    for (const device of DEVICES) {
      await pickDevice(page, device);
      for (const tab of TABS) {
        views.push({ scheme, width, device, tab, found: await violationsOn(page, tab) });
      }
    }
  }
  await context.close();
}
await browser.close();

const bad = views.filter((view) => view.found.length > 0);
for (const view of bad) {
  process.stderr.write(`FAIL ${JSON.stringify(view)}\n`);
}
process.stdout.write(`${views.length} views checked, ${bad.length} with violations\n`);
process.exit(bad.length === 0 ? 0 : 1);
