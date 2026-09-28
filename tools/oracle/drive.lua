WATCH = nil
local plan = {}
for line in io.lines(os.getenv("ORACLE_PLAN")) do
  local f, a, x = line:match("^(%d+)%s+(%S+)%s*(.*)$")
  if f then plan[#plan + 1] = {tonumber(f), a, x} end
end
local pad = manager.machine.ioport.ports[":ctrl1:joypad:JOYPAD"]
local held = {}
local LO = {{1,1,1,0,0,1,0},{1,1,0,0,1,1,0},{1,1,0,1,1,0,0},{1,0,0,0,0,1,0},{1,0,1,1,1,0,0},{1,0,0,1,1,1,0},{1,0,1,0,0,0,0},{1,0,0,0,1,0,0},{1,0,0,1,0,0,0},{1,1,1,0,1,0,0}}
local LE = {{1,0,1,1,0,0,0},{1,0,0,1,1,0,0},{1,1,0,0,1,0,0},{1,0,1,1,1,1,0},{1,1,0,0,0,1,0},{1,0,0,0,1,1,0},{1,1,1,1,0,1,0},{1,1,0,1,1,1,0},{1,1,1,0,1,1,0},{1,1,0,1,0,0,0}}
local RE = {{0,0,0,1,1,0,1},{0,0,1,1,0,0,1},{0,0,1,0,0,1,1},{0,1,1,1,1,0,1},{0,1,0,0,0,1,1},{0,1,1,0,0,0,1},{0,1,0,1,1,1,1},{0,1,1,1,0,1,1},{0,1,1,0,1,1,1},{0,0,0,1,0,1,1}}
local PAR = {{1,1,1,1,1,1},{1,1,0,1,0,0},{1,1,0,0,1,0},{1,1,0,0,0,1},{1,0,1,1,0,0},{1,0,0,1,1,0},{1,0,0,0,1,1},{1,0,1,0,1,0},{1,0,1,0,0,1},{1,0,0,1,0,1}}
local function reader_items()
  local dev = manager.machine.devices[os.getenv("READER") or ":nes_slot:datach:datach"]
  local items = dev.items
  return function(name) return emu.item(items[name]) end
end
local function digits(code)
  local d = {}
  for i = 1, #code do d[i] = tonumber(code:sub(i, i)) end
  return d
end
local function pattern(code)
  local d = digits(code)
  local px = {0, 1, 0}
  local function put(t) for _, v in ipairs(t) do px[#px + 1] = v end end
  if #d == 13 then
    for i = 2, 7 do if PAR[d[1] + 1][i - 1] == 1 then put(LO[d[i] + 1]) else put(LE[d[i] + 1]) end end
    put({1, 0, 1, 0, 1})
    for i = 8, 12 do put(RE[d[i] + 1]) end
    put(RE[d[13] + 1])
  else
    for i = 1, 4 do put(LO[d[i] + 1]) end
    put({1, 0, 1, 0, 1})
    for i = 5, 7 do put(RE[d[i] + 1]) end
    put(RE[d[8] + 1])
  end
  put({0, 1, 0})
  return px
end
local QUIET = 61
local swiping = nil
local function swipe(arg)
  local code, period = arg:match("^(%d+)%s+([%d%.]+)$")
  local px = pattern(code)
  local stream = {}
  for _ = 1, QUIET do stream[#stream + 1] = 1 end
  for _, v in ipairs(px) do stream[#stream + 1] = v end
  for _ = 1, QUIET do stream[#stream + 1] = 1 end
  local start = manager.machine.time:as_double()
  local seconds = tonumber(period) / 1000000
  local mem = manager.machine.devices[":maincpu"].spaces["program"]
  swiping = mem:install_read_tap(0x6000, 0x7fff, "swipe", function(offset, data, mask)
    local index = math.floor((manager.machine.time:as_double() - start) / seconds) + 1
    local pixel = stream[index] or 0
    return (data & 0xf7) | (pixel << 3)
  end)
  print("SWIPED", code, period, #stream)
end
local function scan(code)
  local d = digits(code)
  local px = pattern(code)
  local item = reader_items()
  for i = 1, #d do item("0/DATACH/m_byte_data"):write(i - 1, d[i]) end
  for i = 1, #px do item("0/DATACH/m_pixel_data"):write(i - 1, px[i]) end
  item("0/DATACH/m_byte_length"):write(0, #d)
  item("0/DATACH/m_pixel_length"):write(0, #px)
  item("0/DATACH/m_pixel_count"):write(0, 0)
  item("0/DATACH/m_byte_count"):write(0, 0)
  item("0/DATACH/m_new_code"):write(0, 1)
  print("SCANNED", code, #px)
end
local BBII_PRESENT = 24
local BBII_FIRST = 16
local BBII_LAST = 80
local bbii = {armed = false, k = 0, stream = {}, taps = {}}
local function bbii_stream(code)
  local s = {}
  for idx = BBII_FIRST, 27 do s[#s + 1] = idx == BBII_PRESENT and 1 or 0 end
  for i = #code, 1, -1 do
    local d = tonumber(code:sub(i, i))
    for b = 3, 0, -1 do s[#s + 1] = (d >> b) & 1 end
  end
  return s
end
local function bbscan(code)
  local mem = manager.machine.devices[":maincpu"].spaces["program"]
  if #bbii.taps == 0 then
    local function frame(offset, data, mask)
      bbii.k = 0
      return data
    end
    local function strobe(offset, data, mask)
      bbii.latch = (data & 1) == 1
      if bbii.latch then bbii.k = -BBII_FIRST end
      return data
    end
    local function port(offset, data, mask)
      if not bbii.armed or bbii.latch then return data end
      if bbii.k < 0 then bbii.k = bbii.k + 1; return data end
      local bit = bbii.stream[bbii.k + 1] or 0
      bbii.k = bbii.k + 1
      if bbii.k >= BBII_LAST - BBII_FIRST then bbii.armed = false end
      return (data & 0xfe) | bit
    end
    for _, mirror in ipairs({0x00, 0x80}) do
      for bank = mirror, mirror + 0x3f do
        local base = bank * 0x10000
        bbii.taps[#bbii.taps + 1] = mem:install_read_tap(base + 0x421b, base + 0x421b, "bbii_frame_" .. bank, frame)
        bbii.taps[#bbii.taps + 1] = mem:install_write_tap(base + 0x4016, base + 0x4016, "bbii_strobe_" .. bank, strobe)
        bbii.taps[#bbii.taps + 1] = mem:install_read_tap(base + 0x4017, base + 0x4017, "bbii_port_" .. bank, port)
      end
    end
  end
  bbii.stream = bbii_stream(code)
  bbii.k = 0
  bbii.armed = true
  print("BBSCANNED", code)
end
local caught = {}
local function catch(address)
  local mem = manager.machine.devices[":maincpu"].spaces["program"]
  local low = tonumber(address, 16)
  local function report(offset, data, mask)
    print(string.format("CATCH %s %02x", address, data & 0xff))
    return data
  end
  caught[#caught + 1] = mem:install_write_tap(low, low, "catch_low_" .. address, report)
  caught[#caught + 1] = mem:install_write_tap(0x7e0000 | low, 0x7e0000 | low, "catch_wram_" .. address, report)
end
local function breakpoint(arg)
  local address, label = arg:match("^(%x+)%s+(%S+)$")
  manager.machine.debugger:command("bpset " .. address .. ',1,{printf "HIT ' .. label .. ' %02x",a&ff; g}')
  manager.machine.debugger:command("g")
end
local function flush_hits()
  if not manager.machine.debugger then return end
  for _, line in ipairs(manager.machine.debugger.consolelog) do
    if line:match("^HIT ") then print(line) end
  end
end
local n = 0
emu.register_frame_done(function()
  n = n + 1
  for _, step in ipairs(plan) do
    if step[1] == n then
      local a, x = step[2], step[3]
      if a == "press" then local f = pad.fields["P1 " .. x]; if not f then print("NOFIELD", x); manager.machine:exit() else f:set_value(1); held["P1 " .. x] = n + 6 end end
      if a == "scan" then scan(x) end
      if a == "swipe" then swipe(x) end
      if a == "bbscan" then bbscan(x) end
      if a == "catch" then catch(x) end
      if a == "bp" then breakpoint(x) end
      if a == "poke" then
        local address, value = x:match("^(%x+)%s+(%x+)$")
        manager.machine.devices[":maincpu"].spaces["program"]:write_u8(tonumber(address, 16), tonumber(value, 16))
      end
      if a == "snap" then manager.machine.video:snapshot(); print("SNAP", n, x) end
      if a == "dumpram" then
        local mem = manager.machine.devices[":maincpu"].spaces["program"]
        local out = io.open(x, "wb")
        for addr = 0, 0x7ff do out:write(string.char(mem:read_u8(addr))) end
        out:close(); print("RAM", n, x)
      end
      if a == "watchwrite" then
        local lo, hi = x:match("(%x+)%-(%x+)")
        local mem = manager.machine.devices[":maincpu"].spaces["program"]
        local cpu = manager.machine.devices[":maincpu"]
        local items = manager.machine.devices[":nes_slot:datach"].items
        local bank = emu.item(items["0/m_prg_bank"])
        WATCH = mem:install_write_tap(tonumber(lo, 16), tonumber(hi, 16), "w", function(offset, data, mask)
          print(string.format("WRITE %04x=%02x pc=%04x bank=%d frame=%d", offset, data, cpu.state["PC"].value, bank:read(0), n))
          return data
        end)
      end
      if a == "report" then
        local mem = manager.machine.devices[":maincpu"].spaces["program"]
        local function w(addr) return mem:read_u8(addr) | (mem:read_u8(addr + 1) << 8) end
        print(string.format("REPORT %s type=%d char=%d level=%d hp=%d bp=%d dp=%d", x, mem:read_u8(0x03d0), mem:read_u8(0x0407), mem:read_u8(0x0416), w(0x0417) * 10, w(0x0419) * 10, w(0x041b) * 10))
      end
      if a == "peek" then
        local mem = manager.machine.devices[":maincpu"].spaces["program"]
        local lo, len = x:match("(%x+)%s+(%d+)")
        local bytes = {}
        for i = 0, tonumber(len) - 1 do bytes[#bytes + 1] = string.format("%02x", mem:read_u8(tonumber(lo, 16) + i)) end
        print("PEEK " .. lo .. " " .. table.concat(bytes, " "))
      end
      if a == "exit" then flush_hits(); manager.machine:exit() end
    end
  end
  for k, until_frame in pairs(held) do
    if n >= until_frame then pad.fields[k]:set_value(0); held[k] = nil end
  end
end)
