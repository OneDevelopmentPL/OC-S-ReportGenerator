import json
import subprocess
import re

def get_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except: return "Unknown"

def parse_pci(filter_str):
    line = get_cmd(f"lspci -nn | grep -i '{filter_str}' | head -n 1")
    if line == "Unknown" or not line:
        return {"Device ID": "0000-0000", "Manufacturer": "Unknown"}
    
    match = re.search(r'\[([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\]', line)
    if match:
        dev_id = f"{match.group(1)}-{match.group(2)}".upper()
    else:
        dev_id = "0000-0000"
        
    vendor_id = match.group(1) if match else ""
    vendor = "Intel" if "8086" in vendor_id else "AMD" if vendor_id in ["1002", "1022"] else "NVIDIA" if "10de" in vendor_id else "Unknown"
    
    return {"Device ID": dev_id, "Manufacturer": vendor}

cpu_raw = get_cmd("lscpu | grep 'Model name' | cut -d: -f2").strip()
gpu_info = parse_pci("VGA")
net_info = parse_pci("Ethernet")
usb_info = parse_pci("USB")
storage_info = parse_pci("SATA\\|NVMe")

report = {
    "Motherboard": {
        "Name": get_cmd("cat /sys/class/dmi/id/board_name"),
        "Chipset": "Unknown",
        "Platform": "Desktop"
    },
    "BIOS": {
        "Firmware Type": "UEFI",
        "Secure Boot": "Disabled"
    },
    "CPU": {
        "Manufacturer": "Intel" if "Intel" in get_cmd("lscpu") else "AMD",
        "Processor Name": cpu_raw if cpu_raw else "Intel Core",
        "Codename": "Unknown", 
        "Core Count": get_cmd("nproc"),
        "CPU Count": "1",
        "SIMD Features": "SSE4.2, AVX2"
    },
    "GPU": { "Item 0": { 
        "Manufacturer": gpu_info["Manufacturer"], 
        "Codename": "Unknown", 
        "Device ID": gpu_info["Device ID"], 
        "Device Type": "Integrated GPU" if gpu_info["Manufacturer"] == "Intel" else "Discrete GPU"
    }},
    "Network": { "Item 0": { 
        "Bus Type": "PCI", 
        "Device ID": net_info["Device ID"] 
    }},
    "USB Controllers": { "Item 0": { 
        "Bus Type": "PCI", 
        "Device ID": usb_info["Device ID"] 
    }},
    "Input": { 
        "Item 0": { "Bus Type": "USB" },
        "Item 1": { "Bus Type": "USB" }
    },
    "Storage Controllers": { "Item 0": { 
        "Bus Type": "PCI", 
        "Device ID": storage_info["Device ID"] 
    }}
}

with open('Report.json', 'w') as f:
    json.dump(report, f, indent=4)

print("Report.json generated. If there are some issues, create an issue on GitHub (https://github.com/OneDevelopmentPL/OC-S-ReportGenerator)")
