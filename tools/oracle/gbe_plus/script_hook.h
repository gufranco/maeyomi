#ifndef NDS_SCRIPT_HOOK
#define NDS_SCRIPT_HOOK

#include <cstdlib>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

struct script_event
{
	unsigned frame;
	std::string verb;
	std::vector<std::string> args;
};

struct script_state
{
	bool loaded = false;
	unsigned frame = 0;
	unsigned last_line = 0;
	std::vector<script_event> events;
	std::map<unsigned, std::vector<std::string>> releases;
};

static script_state script;

static void script_load()
{
	script.loaded = true;
	const char* path = std::getenv("GBE_SCRIPT");
	if(path == nullptr) { return; }
	std::ifstream file(path);
	std::string line;
	while(std::getline(file, line))
	{
		std::istringstream words(line);
		script_event event;
		if(!(words >> event.frame >> event.verb)) { continue; }
		std::string arg;
		while(words >> arg) { event.args.push_back(arg); }
		script.events.push_back(event);
	}
}

static unsigned script_key(const std::string& name)
{
	if(name == "a") { return config::gbe_key_a; }
	if(name == "b") { return config::gbe_key_b; }
	if(name == "x") { return config::gbe_key_x; }
	if(name == "y") { return config::gbe_key_y; }
	if(name == "start") { return config::gbe_key_start; }
	if(name == "select") { return config::gbe_key_select; }
	if(name == "up") { return config::gbe_key_up; }
	if(name == "down") { return config::gbe_key_down; }
	if(name == "left") { return config::gbe_key_left; }
	if(name == "right") { return config::gbe_key_right; }
	if(name == "l") { return config::gbe_key_l_trigger; }
	return config::gbe_key_r_trigger;
}

static void script_touch(NTR_core& core, bool down, unsigned x, unsigned y)
{
	if(down)
	{
		core.core_pad.mouse_x = x;
		core.core_pad.mouse_y = y;
		core.core_pad.ext_key_input &= ~0x40;
		return;
	}
	core.core_pad.ext_key_input |= 0x40;
	core.core_pad.mouse_x = 0;
	core.core_pad.mouse_y = 0xFFF;
}

static void script_card(NTR_core& core, const std::string& text)
{
	if(core.core_mmu.current_slot2_device == NTR_MMU::SLOT2_HCV_1000)
	{
		core.core_mmu.hcv.data.assign(text.begin(), text.end());
		while(core.core_mmu.hcv.data.size() < 16) { core.core_mmu.hcv.data.push_back(0x5F); }
		core.core_mmu.hcv.cnt &= ~0x80;
	}
	if(config::mic_device == MIC_WANTAME)
	{
		config::raw_barcode = text;
		core.core_mmu.wantame_scanner_set_barcode();
	}
	if(config::mic_device == MIC_WAVE_SCANNER)
	{
		core.core_mmu.wave_scanner.barcode = text;
		config::wave_scanner_is_barcode = true;
		core.core_mmu.wave_scanner_set_data();
	}
}

static void script_dump(NTR_core& core, const std::vector<std::string>& args)
{
	unsigned address = std::stoul(args[0], nullptr, 16);
	unsigned length = std::stoul(args[1], nullptr, 16);
	std::ofstream out(args[2], std::ios::binary | std::ios::app);
	for(unsigned offset = 0; offset < length; offset++)
	{
		char byte = static_cast<char>(core.core_mmu.read_u8(address + offset));
		out.write(&byte, 1);
	}
}

static void script_shot(NTR_core& core, const std::string& path)
{
	std::ofstream out(path, std::ios::binary);
	out << "P6\n256 384\n255\n";
	const std::vector<u32>& pixels = core.core_cpu_nds9.controllers.video.screen_buffer;
	for(unsigned index = 0; index < 256 * 384; index++)
	{
		char rgb[3] = {
			static_cast<char>((pixels[index] >> 16) & 0xFF),
			static_cast<char>((pixels[index] >> 8) & 0xFF),
			static_cast<char>(pixels[index] & 0xFF),
		};
		out.write(rgb, 3);
	}
}

static void script_apply(NTR_core& core, const script_event& event)
{
	if(event.verb == "press")
	{
		unsigned hold = event.args.size() > 1 ? std::stoul(event.args[1]) : 6;
		core.core_pad.process_keyboard(script_key(event.args[0]), true);
		script.releases[script.frame + hold].push_back("key " + event.args[0]);
	}
	else if(event.verb == "touch")
	{
		unsigned hold = event.args.size() > 2 ? std::stoul(event.args[2]) : 6;
		script_touch(core, true, std::stoul(event.args[0]), std::stoul(event.args[1]));
		script.releases[script.frame + hold].push_back("touch");
	}
	else if(event.verb == "card") { script_card(core, event.args.empty() ? "" : event.args[0]); }
	else if(event.verb == "dump") { script_dump(core, event.args); }
	else if(event.verb == "shot") { script_shot(core, event.args[0]); }
	else if(event.verb == "exit") { std::exit(0); }
}

static void script_tick(NTR_core& core)
{
	if(!script.loaded) { script_load(); }
	script.frame++;
	auto pending = script.releases.find(script.frame);
	if(pending != script.releases.end())
	{
		for(const std::string& release : pending->second)
		{
			if(release == "touch") { script_touch(core, false, 0, 0); }
			else { core.core_pad.process_keyboard(script_key(release.substr(4)), false); }
		}
		script.releases.erase(pending);
	}
	for(const script_event& event : script.events)
	{
		if(event.frame == script.frame) { script_apply(core, event); }
	}
}

#endif
