local mem = manager.machine.devices[":maincpu"].spaces["program"]
local cpu = manager.machine.devices[":maincpu"]
local BYTE_S, GAP_S = 0.001, 0.002
local REPLY = {0xff, 0xff, 0x10, 0x07}
local RECORD, RECORD_LEN = tonumber(os.getenv("RECORD_ADDR") or "0xc99e"), tonumber(os.getenv("RECORD_LEN") or "0x31")
local STATUS = tonumber(os.getenv("STATUS_ADDR") or "0xc834")
local READY_FRAME = tonumber(os.getenv("READY_FRAME") or "1480")
local SETTLE = tonumber(os.getenv("SETTLE") or "90")
local codes = {}
for line in io.lines(os.getenv("CODES")) do if line:match("^%d+$") then codes[#codes + 1] = line end end
local frame, internal, sb, armed, delivered = 0, 0, 0xff, false, false
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
  if v == 0x81 then sb = REPLY[(internal % 4) + 1]; internal = internal + 1; armed = false
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
local function dump(code)
  local s = ""
  for i = 0, RECORD_LEN - 1 do s = s .. string.format("%02x", mem:read_u8(RECORD + i)) end
  print(string.format("REC %s %02x %s", code, mem:read_u8(STATUS), s))
end
local function start_next()
  index = index + 1
  if index > #codes then print("DONE"); manager.machine:exit(); return end
  manager.machine:load("ready")
  phase, wait = "loading", 2
end
emu.register_frame_done(function()
  frame = frame + 1
  if phase == "boot" then
    local p = frame % 180
    fields["Start"]:set_value((p >= 60 and p < 70) and 1 or 0)
    fields["Button A"]:set_value((p >= 120 and p < 130) and 1 or 0)
    if frame == READY_FRAME then
      fields["Start"]:set_value(0); fields["Button A"]:set_value(0)
      manager.machine:save("ready")
      phase, wait = "saving", 2
    end
  elseif phase == "saving" then
    wait = wait - 1
    if wait <= 0 then start_next() end
  elseif phase == "loading" then
    wait = wait - 1
    if wait <= 0 then
      build(codes[index])
      armed, delivered, sent, scanning, sb = true, false, 0, true, 0xff
      mem:write_u8(STATUS, 0xee)
      next_at = now()
      phase, wait = "scanning", SETTLE
    end
  elseif phase == "scanning" then
    wait = wait - 1
    if wait <= 0 then scanning = false; dump(codes[index]); start_next() end
  end
end)
