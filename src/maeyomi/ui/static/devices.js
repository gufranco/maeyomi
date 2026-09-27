const DEVICE_KEY = 'maeyomi-device';
const SECOND_DEVICE = 'bb2';
const DBZ_DEVICE = 'dbz';
const STAT_KEYS = ['hp', 'st', 'df'];

let deviceList = [];
let dbzList = [];
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

function savedDevice() {
  try {
    return window.localStorage.getItem(DEVICE_KEY) ?? SECOND_DEVICE;
  } catch {
    return SECOND_DEVICE;
  }
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

const DEVICE_GROUPS = [['machine', 'device.machines'], ['game', 'device.games']];

function deviceOptionsHtml(group) {
  const label = (device) => (isJapanese() ? device.japanese : device.english);
  return deviceList
    .filter((device) => device.group === group)
    .map((device) => ({ value: device.key, label: label(device) }))
    .toSorted((first, second) => first.label.localeCompare(second.label, currentLanguage))
    .map((option) => optionHtml(option.value, option.label, chosenDevice))
    .join('');
}

function renderDeviceOptions() {
  $('device').replaceChildren();
  $('device').insertAdjacentHTML(
    'afterbegin',
    DEVICE_GROUPS.map(([group, key]) =>
      `<optgroup label="${escapeHtml(t(key))}">${deviceOptionsHtml(group)}</optgroup>`).join(''),
  );
}

function renderDevices() {
  renderDeviceOptions();
  renderDbzChoices();
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

function applySliders(form) {
  const limits = { hp: form.hp_max, st: form.st_max, df: form.df_max };
  STAT_KEYS.forEach((key) => {
    $(key).setAttribute('max', String(limits[key]));
    $(key).setAttribute('step', String(form.steps[STAT_KEYS.indexOf(key)]));
    $(key).dispatchEvent(new Event('input'));
  });
}

function applyDeviceForm() {
  const form = deviceForm();
  if (!form) return;
  document.querySelectorAll('[data-device-field]').forEach((node) => {
    node.toggleAttribute('hidden', !form.fields.includes(node.dataset.deviceField));
  });
  const detailShown = [...$('one-detail').querySelectorAll('[data-device-field]')]
    .some((node) => !node.hidden);
  $('one-detail').toggleAttribute('hidden', !detailShown);
  applySliders(form);
  applySheetForm(form);
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
  $('device').addEventListener('change', () => chooseDevice($('device').value));
}

function deviceCardPayload() {
  const job = reads('job') && $('job').value !== '';
  const character = reads(DBZ_DEVICE) && $('dbz-character').value;
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
    ...(character ? { character: $('dbz-character').value } : {}),
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
  if (!ok) return;
  cheatCard = { barcode: body.barcode, name: body.name, device: chosenDevice };
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
