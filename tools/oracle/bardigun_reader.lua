local cpu = manager.machine.devices[":maincpu"]
local mem = cpu.spaces["program"]
fields = {}
for _, port in pairs(manager.machine.ioport.ports) do
  for name, field in pairs(port.fields) do fields[name] = field end
end
local CODE = os.getenv("CODE")
local SCAN_FRAME = tonumber(os.getenv("SCAN_FRAME") or "4400")
local READ_FRAME = tonumber(os.getenv("READ_FRAME") or "5600")
local SPECIES = tonumber(os.getenv("SPECIES_ADDR") or "0xcaac")
local RECORD = tonumber(os.getenv("RECORD_ADDR") or "0xcae4")
local RECORD_LEN = tonumber(os.getenv("RECORD_LEN") or "22")
local BITS, QUIET, LEAD = 15, 20, 8
local steps = {}
for item in (os.getenv("STEPS") or ""):gmatch("[^,]+") do
  local at, button = item:match("^(%d+):(.+)$")
  steps[tonumber(at)] = button
end
local L = {"0001101","0011001","0010011","0111101","0100011","0110001","0101111","0111011","0110111","0001011"}
local G = {"0100111","0110011","0011011","0100001","0011101","0111001","0000101","0010001","0001001","0010111"}
local R = {"1110010","1100110","1101100","1000010","1011100","1001110","1010000","1000100","1001000","1110100"}
local P = {"LLLLLL","LLGLGG","LLGGLG","LLGGGL","LGLLGG","LGGLLG","LGGGLL","LGLGLG","LGLGGL","LGGLGL"}
local function modules(code)
  local d = {}
  for i = 1, #code do d[i] = tonumber(code:sub(i, i)) end
  local s = string.rep("0", QUIET) .. "101"
  if #code == 8 then
    for i = 1, 4 do s = s .. L[d[i] + 1] end
    s = s .. "01010"
    for i = 5, 8 do s = s .. R[d[i] + 1] end
  else
    local parity = P[d[1] + 1]
    for i = 2, 7 do s = s .. ((parity:sub(i - 1, i - 1) == "L") and L or G)[d[i] + 1] end
    s = s .. "01010"
    for i = 8, 13 do s = s .. R[d[i] + 1] end
  end
  return s .. "101" .. string.rep("0", QUIET)
end
local stream, pos = {}, 0
local function build(code)
  local bits = {}
  for m in modules(code):gmatch(".") do
    for _ = 1, BITS do bits[#bits + 1] = (m == "0") and 1 or 0 end
  end
  for _ = 1, LEAD do stream[#stream + 1] = 0x00 end
  for i = 1, #bits, 8 do
    local byte = 0
    for j = 0, 7 do byte = (byte << 1) | (bits[i + j] or 1) end
    stream[#stream + 1] = byte
  end
  for _ = 1, 64 do stream[#stream + 1] = 0xff end
end
local sb, active, frame = 0xff, false, 0
sctap = mem:install_write_tap(0xff02, 0xff02, "sc", function(offset, data, mask)
  if (data & 0x81) == 0x81 then
    if active and pos < #stream then pos = pos + 1; sb = stream[pos] else sb = active and 0xff or 0x00 end
  end
end)
sbtap = mem:install_read_tap(0xff01, 0xff01, "sb", function(offset, data, mask) return sb end)
local held, release = nil, 0
emu.register_frame_done(function()
  frame = frame + 1
  if held and frame >= release then fields[held]:set_value(0); held = nil end
  if steps[frame] then held = steps[frame]; fields[held]:set_value(1); release = frame + 6 end
  if frame == SCAN_FRAME then build(CODE); active = true end
  if frame == READ_FRAME then
    local record = ""
    for i = 0, RECORD_LEN - 1 do record = record .. string.format("%02x", mem:read_u8(RECORD + i)) end
    print(string.format("REC %s %02x %d %s", CODE, mem:read_u8(SPECIES), pos, record))
    manager.machine:exit()
  end
end)
