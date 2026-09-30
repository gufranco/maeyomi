local mem = manager.machine.devices[":maincpu"].spaces["program"]
local cpu = manager.machine.devices[":maincpu"]
local BYTE_S, GAP_S = 0.001, 0.002
local REPLY = {0xff, 0xff, 0x10, 0x07}
local SILENT = os.getenv("SILENT_REPLY") ~= nil
local RECORD, RECORD_LEN = tonumber(os.getenv("RECORD_ADDR") or "0xc99e"), tonumber(os.getenv("RECORD_LEN") or "0x31")
local STATUS = tonumber(os.getenv("STATUS_ADDR") or "0xc834")
local READY_FRAME = tonumber(os.getenv("READY_FRAME") or "1480")
local SETTLE = tonumber(os.getenv("SETTLE") or "90")
local POKE_ADDR, POKE_VALUE = tonumber(os.getenv("POKE_ADDR") or ""), tonumber(os.getenv("POKE_VALUE") or "")
BOOT_STEPS = {}
for item in (os.getenv("BOOT_STEPS") or ""):gmatch("[^,]+") do
  local at, button = item:match("(%d+):(.+)")
  BOOT_STEPS[tonumber(at)] = button
end
local PRESS_FRAMES = 6
local held, release = nil, 0
local codes = {}
for line in io.lines(os.getenv("CODES")) do if line:match("^%d+$") then codes[#codes + 1] = line end end
local frame, internal, sb, armed, delivered = 0, 0, 0xff, false, false
local saved_internal, saved_armed, last_time = 0, false, 0
local SAVE_WAIT = 10
local function rewound()
  local t = manager.machine.time:as_double()
  if t < last_time then internal, armed, delivered = saved_internal, saved_armed, false end
  last_time = t
end
local stream, gaps, sent, scanning, next_at = {}, {}, 0, false, 0
local index, phase, wait = 0, "boot", 0
fields = {}
for _, port in pairs(manager.machine.ioport.ports) do for name, field in pairs(port.fields) do fields[name] = field end end
local function now() return manager.machine.time:as_double() end
local function build(code)
  stream, gaps = {}, {}
  for _ = 1, 2 do
    stream[#stream + 1] = 0x02
    for i = 1, #code do stream[#stream + 1] = code:byte(i) end
    stream[#stream + 1] = 0x03
    gaps[#stream] = true
  end
end
local function deliver()
  sent = sent + 1
  sb = stream[sent]
  delivered = true
  mem:write_u8(0xff0f, mem:read_u8(0xff0f) | 0x08)
  next_at = now() + (gaps[sent] and GAP_S or BYTE_S)
end
wtap = mem:install_write_tap(0xff02, 0xff02, "sc", function(offset, data, mask)
  local v = data & 0xff
  rewound()
  if v == 0x81 then sb = SILENT and 0xff or REPLY[(internal % 4) + 1]; internal = internal + 1; armed = false
  elseif v == 0x80 then armed = true; delivered = false end
end)
rtap = mem:install_read_tap(0xff01, 0xff01, "sb", function(offset, data, mask) return sb end)
sctap = mem:install_read_tap(0xff02, 0xff02, "scr", function(offset, data, mask)
  if delivered then return data & 0x7f end
  return data
end)
pumptap = mem:install_read_tap(0xc000, 0xdfff, "pump", function(offset, data, mask)
  if scanning and armed and not delivered and sent < #stream and now() >= next_at then deliver() end
end)
local function record()
  local s = ""
  for i = 0, RECORD_LEN - 1 do s = s .. string.format("%02x", mem:read_u8(RECORD + i)) end
  return s
end
local CAPTURE_ADDR = tonumber(os.getenv("CAPTURE_ADDR") or "")
local CAPTURE_PC = tonumber(os.getenv("CAPTURE_PC") or "")
local CAPTURE_BANK = tonumber(os.getenv("CAPTURE_BANK") or "1")
local CAPTURE_SPAN = 8
local captured, bank = nil, 1
if CAPTURE_ADDR and CAPTURE_PC then
  banktap = mem:install_write_tap(0x2000, 0x3fff, "bank", function(offset, data, mask) bank = data & 0xff end)
  capturetap = mem:install_write_tap(CAPTURE_ADDR, CAPTURE_ADDR, "capture", function(offset, data, mask)
    local pc = cpu.state["PC"].value
    if scanning and captured == nil and bank == CAPTURE_BANK and pc >= CAPTURE_PC and pc < CAPTURE_PC + CAPTURE_SPAN then
      captured = record()
    end
  end)
end
PEEKS = {}
for item in (os.getenv("PEEK_ADDRS") or ""):gmatch("[^,]+") do PEEKS[#PEEKS + 1] = tonumber(item) end
POST_STEPS = {}
for item in (os.getenv("POST_STEPS") or ""):gmatch("[^,]+") do
  local at, button = item:match("^(%d+):(.+)$")
  POST_STEPS[tonumber(at)] = button
end
local post_held, post_release = nil, 0
local function peeks()
  if #PEEKS == 0 then return "" end
  local s = ""
  for _, address in ipairs(PEEKS) do s = s .. string.format("%02x", mem:read_u8(address)) end
  return " " .. s
end
local function dump(code)
  if #PEEKS > 0 then
    print(string.format("REC %s %02x %s%s", code, mem:read_u8(STATUS), record(), peeks()))
    return
  end
  if CAPTURE_ADDR and CAPTURE_PC then
    print(string.format("REC %s %s %s", code, captured and "00" or "ee", captured or record()))
    return
  end
  print(string.format("REC %s %02x %s", code, mem:read_u8(STATUS), record()))
end
local function start_next()
  index = index + 1
  if index > #codes then print("DONE"); manager.machine:exit(); return end
  manager.machine:load("ready")
  phase, wait = "loading", 2
end
emu.register_frame_done(function()
  frame = frame + 1
  rewound()
  if phase == "boot" then
    if next(BOOT_STEPS) then
      if held and frame >= release then fields[held]:set_value(0); held = nil end
      if BOOT_STEPS[frame] then held = BOOT_STEPS[frame]; fields[held]:set_value(1); release = frame + PRESS_FRAMES end
    else
      local p = frame % 180
      fields["Start"]:set_value((p >= 60 and p < 70) and 1 or 0)
      fields["Button A"]:set_value((p >= 120 and p < 130) and 1 or 0)
    end
    if frame == READY_FRAME then
      fields["Start"]:set_value(0); fields["Button A"]:set_value(0)
      if held then fields[held]:set_value(0); held = nil end
      manager.machine:save("ready")
      saved_internal, saved_armed = internal, armed
      phase, wait = "saving", SAVE_WAIT
    end
  elseif phase == "saving" then
    wait = wait - 1
    if wait <= 0 then start_next() end
  elseif phase == "loading" then
    wait = wait - 1
    if wait <= 0 then
      build(codes[index])
      if POKE_ADDR and POKE_VALUE then mem:write_u8(POKE_ADDR, POKE_VALUE) end
      delivered, sent, scanning, sb, captured = false, 0, true, 0xff, nil
      mem:write_u8(STATUS, 0xee)
      next_at = now()
      phase, wait = "scanning", SETTLE
    end
  elseif phase == "scanning" then
    wait = wait - 1
    local elapsed = SETTLE - wait
    if post_held and elapsed >= post_release then fields[post_held]:set_value(0); post_held = nil end
    if POST_STEPS[elapsed] then post_held = POST_STEPS[elapsed]; fields[post_held]:set_value(1); post_release = elapsed + PRESS_FRAMES end
    if wait <= 0 then
      if post_held then fields[post_held]:set_value(0); post_held = nil end
      scanning = false; dump(codes[index]); start_next()
    end
  end
end)
