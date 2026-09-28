const DEVICE_KEY = 'maeyomi-device';
const DEVICE_PARAM = 'device';
const SECOND_DEVICE = 'bb2';
const DBZ_DEVICE = 'dbz';
const STAT_KEYS = ['hp', 'st', 'df'];

let deviceList = [];
let dbzList = [];
let gameList = [];
let chosenDevice = SECOND_DEVICE;

const currentDevice = () => chosenDevice;

const isSecond = () => chosenDevice === SECOND_DEVICE;

const deviceForm = () => deviceList.find((device) => device.key === chosenDevice);

const deviceName = () => {
  const device = deviceForm();
  if (!device) return '';
  return isJapanese() ? device.japanese : device.english;
};

const reads = (field) => deviceForm()?.fields.includes(field) ?? false;

const readsOnSheet = (field) => deviceForm()?.sheet_fields.includes(field) ?? false;

const SHEET_KEYS = ['hp', 'st', 'df'];

function deviceFromAddress() {
  return new URLSearchParams(window.location.search).get(DEVICE_PARAM);
}

function savedDevice() {
  const linked = deviceFromAddress();
  if (linked) return linked;
  try {
    return window.localStorage.getItem(DEVICE_KEY) ?? SECOND_DEVICE;
  } catch {
    return SECOND_DEVICE;
  }
}

function addressDevice(key) {
  if (deviceFromAddress() === key) return;
  const query = `?${DEVICE_PARAM}=${encodeURIComponent(key)}`;
  window.history.pushState(null, '', `${window.location.pathname}${query}${window.location.hash}`);
}

function rememberDevice() {
  try {
    window.localStorage.setItem(DEVICE_KEY, chosenDevice);
  } catch {
    document.documentElement.dataset.deviceNotRemembered = 'true';
  }
}

function dbzOptionHtml(entry, chosen) {
  const label = isJapanese() ? entry.japanese : entry.english;
  const value = String(entry.id);
  return `<option value="${value}"${value === chosen ? ' selected' : ''}>` +
    `${escapeHtml(label)}</option>`;
}

function renderDbzChoices() {
  const chosen = $('dbz-character').value;
  const group = (kind, key) =>
    `<optgroup label="${escapeHtml(t(key))}">` +
    dbzList.filter((entry) => entry.kind === kind).map((entry) => dbzOptionHtml(entry, chosen))
      .join('') + '</optgroup>';
  $('dbz-character').replaceChildren();
  $('dbz-character').insertAdjacentHTML(
    'afterbegin',
    `<option value="">${escapeHtml(t('dbz.anyone'))}</option>` +
      group('fighter', 'dbz.fighters') + group('item', 'dbz.items'),
  );
}

function renderGameChoices() {
  const chosen = $('game-character').value;
  const kinds = [...new Set(gameList.map((entry) => entry.kind))];
  const group = (kind) =>
    `<optgroup label="${escapeHtml(t(`game.kind.${kind}`))}">` +
    gameList.filter((entry) => entry.kind === kind).map((entry) => dbzOptionHtml(entry, chosen))
      .join('') + '</optgroup>';
  $('game-character').replaceChildren();
  $('game-character').insertAdjacentHTML(
    'afterbegin',
    `<option value="">${escapeHtml(t('game.anyone'))}</option>` + kinds.map(group).join(''),
  );
}

async function loadGameCards() {
  gameList = reads('game') ? await getJson(`/api/game-cards/${chosenDevice}`) : [];
  renderGameChoices();
  await loadGamePicks();
}

function pickFieldHtml(pick) {
  const label = isJapanese() ? pick.japanese : pick.english;
  const options = pick.options.map((option) => {
    const name = isJapanese() ? option.japanese : option.english;
    return `<option value="${escapeHtml(String(option.value))}">${escapeHtml(name)}</option>`;
  }).join('');
  const id = `pick-${pick.key}`;
  return `<p class="field"><label for="${escapeHtml(id)}">${escapeHtml(label)}</label>` +
    `<select id="${escapeHtml(id)}" data-pick="${escapeHtml(pick.key)}">` +
    `<option value="">${escapeHtml(t('game.pick.any'))}</option>${options}</select></p>`;
}

async function loadGamePicks() {
  const chosen = $('game-character').value;
  const picks = reads('picks') && chosen !== ''
    ? await getJson(`/api/game-picks/${chosenDevice}/${encodeURIComponent(chosen)}`)
    : [];
  $('game-picks').replaceChildren();
  $('game-picks').insertAdjacentHTML('afterbegin', picks.map(pickFieldHtml).join(''));
  $('game-picks').toggleAttribute('hidden', picks.length === 0);
}

function chosenPicks() {
  const chosen = [...document.querySelectorAll('[data-pick]')]
    .filter((select) => select.value !== '')
    .map((select) => [select.dataset.pick, Number(select.value)]);
  return Object.fromEntries(chosen);
}

const DEVICE_GROUPS = [
  ['machine', 'device.machines'],
  ['super_famicom', 'device.super_famicom'],
  ['datach', 'device.datach'],
  ['famicom', 'device.famicom'],
];

function deviceButtonHtml(device) {
  const name = isJapanese() ? device.japanese : device.english;
  const current = device.key === chosenDevice;
  return `<li><button type="button" data-device="${escapeHtml(device.key)}"` +
    ` aria-pressed="${current}"${current ? ' aria-current="true"' : ''}>` +
    `<span class="item-name">${escapeHtml(name)}</span>` +
    `<span class="item-summary">${escapeHtml(t(`device.summary.${device.key}`))}</span>` +
    '</button></li>';
}

function deviceGroupHtml(group, key) {
  const label = (device) => (isJapanese() ? device.japanese : device.english);
  const items = deviceList
    .filter((device) => device.platform === group)
    .toSorted((first, second) => label(first).localeCompare(label(second), currentLanguage))
    .map(deviceButtonHtml)
    .join('');
  return `<p class="list-heading">${escapeHtml(t(key))}</p><ul class="item-list">${items}</ul>`;
}

function renderDeviceOptions() {
  $('device').replaceChildren();
  $('device').insertAdjacentHTML(
    'afterbegin',
    DEVICE_GROUPS.map(([group, key]) => deviceGroupHtml(group, key)).join(''),
  );
  const current = deviceList.find((device) => device.key === chosenDevice);
  $('device-current').textContent = current ? (isJapanese() ? current.japanese : current.english) : '';
  filterDevices();
}

function filterDevices() {
  const query = $('device-filter').value.trim().toLocaleLowerCase(currentLanguage);
  document.querySelectorAll('#device .item-list').forEach((list) => {
    const items = [...list.children];
    items.forEach((item) => {
      const text = item.textContent.toLocaleLowerCase(currentLanguage);
      item.toggleAttribute('hidden', query !== '' && !text.includes(query));
    });
    list.previousElementSibling.toggleAttribute('hidden', items.every((item) => item.hidden));
  });
}

function setDeviceMenuOpen(open) {
  $('sidebar').toggleAttribute('data-open', open);
  $('device-toggle').setAttribute('aria-expanded', String(open));
}

function clearCardImage(imageId, placeholderId) {
  const previous = $(imageId).getAttribute('src');
  if (previous) URL.revokeObjectURL(previous);
  $(imageId).removeAttribute('src');
  $(imageId).setAttribute('alt', '');
  $(placeholderId).toggleAttribute('hidden', false);
}

function clearFrame(frameId, placeholderKey) {
  $(frameId).replaceChildren();
  $(frameId).insertAdjacentHTML(
    'afterbegin',
    `<p class="placeholder" data-i18n="${placeholderKey}">${escapeHtml(t(placeholderKey))}</p>`,
  );
}

function startFresh() {
  ['one', 'read'].forEach((form) => $(form).reset());
  clearCardImage('card-image', 'card-placeholder');
  clearCardImage('read-image', 'read-placeholder');
  clearFrame('sheet-frame', 'many.placeholder');
  ['one-status', 'many-status', 'read-status'].forEach((id) => {
    $(id).setAttribute('class', 'status');
    $(id).replaceChildren();
  });
  $('one-code').toggleAttribute('hidden', true);
  $('read-facts').toggleAttribute('hidden', true);
  $('tab-one').click();
  window.scrollTo(0, 0);
}

function switchDevice(key) {
  startFresh();
  chooseDevice(key);
  refreshPreviewSoon();
}

function firstShownDevice() {
  return [...document.querySelectorAll('#device [data-device]')]
    .find((button) => !button.closest('li').hidden)?.dataset.device;
}

function focusDeviceFilter(event) {
  const typing = event.target.closest('input, select, textarea, [contenteditable]');
  if (event.key !== '/' || typing || event.metaKey || event.ctrlKey || event.altKey) return;
  event.preventDefault();
  setDeviceMenuOpen(true);
  $('device-filter').focus();
}

function pickFirstShown(event) {
  const key = firstShownDevice();
  if (event.key !== 'Enter' || !key) return;
  event.preventDefault();
  switchDevice(key);
  addressDevice(key);
  setDeviceMenuOpen(false);
  $('device-filter').value = '';
  filterDevices();
}

function setUpDeviceShortcuts() {
  document.addEventListener('keydown', focusDeviceFilter);
  $('device-filter').addEventListener('keydown', pickFirstShown);
  window.addEventListener('popstate', () => {
    const key = deviceFromAddress() ?? SECOND_DEVICE;
    if (key !== chosenDevice) switchDevice(key);
  });
}

function setUpDeviceMenu() {
  $('device-toggle').addEventListener('click', () => {
    setDeviceMenuOpen(!$('sidebar').hasAttribute('data-open'));
  });
  $('device-filter').addEventListener('input', filterDevices);
  setUpDeviceShortcuts();
  $('sidebar').addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !$('sidebar').hasAttribute('data-open')) return;
    setDeviceMenuOpen(false);
    $('device-toggle').focus();
  });
}

const JOB_NAMES = {
  bb2: [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
  bb1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  double: [0, 0, 0, 0, 2, 0, 3, 1, 1, 1],
};
const JOB_KEYS = ['job.warrior', 'job.magician', 'job.priest', 'job.holy'];

function renderJobOptions() {
  const names = JOB_NAMES[chosenDevice] ?? JOB_NAMES.bb2;
  const chosen = $('job').value;
  const options = names.map((kind, number) => ({
    value: String(number),
    label: t('job.option', { number, name: t(JOB_KEYS[kind]) }),
  }));
  fillSelect('job', [{ value: '', label: t('job.any') }, ...options], chosen || '');
}

function renderDevices() {
  renderDeviceOptions();
  renderDbzChoices();
  renderGameChoices();
  renderJobOptions();
  applyStatLabels();
}

function applyStatLabels() {
  const form = deviceForm();
  if (!form) return;
  STAT_KEYS.forEach((key, index) => {
    [`label[for="${key}"]`, `label[for="${key}-min"]`].forEach((selector) => {
      const label = document.querySelector(selector);
      label.setAttribute('data-i18n', form.stat_keys[index]);
      label.textContent = t(form.stat_keys[index]);
    });
  });
}

function applySheetForm(form) {
  const limits = [form.hp_max, form.st_max, form.df_max];
  SHEET_KEYS.forEach((key, index) => {
    ['min', 'max'].forEach((end, bound) => {
      const input = $(`${key}-${end}`);
      input.setAttribute('max', String(limits[index]));
      input.setAttribute('step', String(form.steps[index]));
      input.setAttribute('value', String(form.ranges[index][bound]));
    });
  });
  $('many').reset();
  document.querySelectorAll('[data-sheet-field]').forEach((node) => {
    node.toggleAttribute('hidden', !form.sheet_fields.includes(node.dataset.sheetField));
  });
}

function sliderLimits(form) {
  const backwards = reads('backRead') && $('backRead').checked && form.back_ranges;
  if (backwards) return form.back_ranges;
  return [[0, form.hp_max], [0, form.st_max], [0, form.df_max]];
}

function applySliders(form) {
  const limits = sliderLimits(form);
  STAT_KEYS.forEach((key, index) => {
    [$(key), $(`${key}-box`)].forEach((control) => {
      control.setAttribute('min', String(limits[index][0]));
      control.setAttribute('max', String(limits[index][1]));
      control.setAttribute('step', String(form.steps[index]));
    });
    $(key).dispatchEvent(new Event('input'));
  });
}

function hideEmptySections() {
  document.querySelectorAll('#one fieldset').forEach((section) => {
    const fields = [...section.querySelectorAll('.field')];
    const shown = fields.some((field) => !field.hidden);
    section.toggleAttribute('hidden', !shown);
  });
  const folded = [...$('one-more').querySelectorAll('fieldset')];
  $('one-more').toggleAttribute('hidden', folded.every((section) => section.hidden));
}

function applyDeviceForm() {
  const form = deviceForm();
  if (!form) return;
  document.querySelectorAll('[data-device-field]').forEach((node) => {
    node.toggleAttribute('hidden', !form.fields.includes(node.dataset.deviceField));
  });
  hideEmptySections();
  applySliders(form);
  applySheetForm(form);
  renderJobOptions();
  applyStatLabels();
  cheatCard = null;
  $('one-code').toggleAttribute('hidden', true);
}

function chooseDevice(key) {
  chosenDevice = deviceList.some((device) => device.key === key) ? key : SECOND_DEVICE;
  renderDeviceOptions();
  rememberDevice();
  applyDeviceForm();
  resetShelf();
  loadOfficial().catch(() => setStatus('official-status', 'bad', 'tag.impossible', t('status.wrong')));
  loadGameCards().catch(() => setStatus('one-status', 'bad', 'tag.impossible', t('status.wrong')));
}

async function setUpDevices() {
  const [devices, dbz] = await Promise.all([
    getJson('/api/devices'),
    getJson('/api/dbz-characters'),
  ]);
  deviceList = devices;
  dbzList = dbz;
  renderDevices();
  chooseDevice(savedDevice());
  setUpDeviceMenu();
  $('device').addEventListener('click', (event) => {
    const button = event.target.closest('[data-device]');
    if (!button) return;
    switchDevice(button.dataset.device);
    addressDevice(button.dataset.device);
    setDeviceMenuOpen(false);
  });
  $('backRead').addEventListener('change', () => applySliders(deviceForm()));
  $('game-character').addEventListener('change', () => {
    loadGamePicks().catch(() => setStatus('one-status', 'bad', 'tag.impossible', t('status.wrong')));
  });
}

function deviceCardPayload() {
  const job = reads('job') && $('job').value !== '';
  const character = (reads(DBZ_DEVICE) && $('dbz-character').value) ||
    (reads('game') && $('game-character').value);
  const level = reads(DBZ_DEVICE) && $('dbz-level').value !== '';
  return {
    device: chosenDevice,
    name: $('name').value || 'Card',
    hp: $('hp').value,
    st: $('st').value,
    df: $('df').value,
    ...(reads('race') ? { race: $('race').value } : {}),
    ...(job ? { job: Number($('job').value) } : {}),
    ...(reads('backRead') ? { backRead: $('backRead').checked } : {}),
    ...(reads('nearest') ? { nearest: $('nearest').checked } : {}),
    ...(character ? { character } : {}),
    ...(reads('picks') ? { picks: chosenPicks() } : {}),
    ...(level ? { level: Number($('dbz-level').value) } : {}),
  };
}

const factLines = (facts) =>
  facts.map((fact) =>
    isJapanese() ? `${fact.label_ja}: ${fact.value_ja}` : `${fact.label}: ${fact.value}`);

function showCode(barcode) {
  $('one-code').toggleAttribute('hidden', false);
  $('one-code-value').textContent = barcode;
}

async function makeDeviceCard() {
  setStatus('one-status', 'info', 'tag.working', t('status.searching', { device: deviceName() }));
  const { ok, body } = await postJson('/api/device-card', deviceCardPayload());
  if (!ok) {
    refuse('one-status', body);
    return null;
  }
  if (body.is_exact) {
    setStatus('one-status', 'good', 'tag.exact', t('status.deviceCard', { device: deviceName() }),
      factLines(body.facts));
  } else {
    setStatus('one-status', 'warn', 'tag.closest', t('status.deviceClosest'), factLines(body.facts));
  }
  showCode(body.barcode);
  await showPreview(body.barcode, $('name').value || 'Card');
  return body;
}

async function activateDeviceCheat(typed) {
  const { ok, body } = await postJson('/api/device-cheat', {
    device: chosenDevice,
    ...(typed ? { name: typed } : {}),
  });
  if (!ok) {
    $('tab-one').click();
    refuse('one-status', body);
    return;
  }
  cheatCard = { barcode: body.barcode, name: body.name, device: chosenDevice, companion: body.companion };
  $('name').value = body.name;
  $('tab-one').click();
  celebrate();
  setStatus('one-status', 'cheat', 'tag.cheat',
    t('status.deviceCheat', { name: body.name, device: deviceName() }), factLines(body.facts));
  showCode(body.barcode);
  await showPreview(body.barcode, body.name);
}

function showDeviceFacts(facts) {
  const rows = facts.map((fact) =>
    isJapanese()
      ? `<dt>${escapeHtml(fact.label_ja)}</dt><dd>${escapeHtml(fact.value_ja)}</dd>`
      : `<dt>${escapeHtml(fact.label)}</dt><dd>${escapeHtml(fact.value)}</dd>`);
  $('read-facts').replaceChildren();
  $('read-facts').insertAdjacentHTML('afterbegin', rows.join(''));
  $('read-facts').toggleAttribute('hidden', false);
}
