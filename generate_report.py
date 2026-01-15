#!/usr/bin/env python3
import json
import subprocess
import re
import os
import webbrowser
import sys
import time

GITHUB_URL = "https://github.com/OneDevelopmentPL/OC-S-ReportGenerator"

def check_root():
    if os.geteuid() != 0:
        print("[!] You must run this script as root (sudo).")
        sys.exit(1)

def get_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return "Unknown"

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

def generate_report():
    print("[*] Generating report...")
    time.sleep(0.5)
    
    print("[*] Detecting CPU...")
    cpu_raw = get_cmd("lscpu | grep 'Model name' | cut -d: -f2").strip()
    cpu_count = get_cmd("nproc")
    print(f"    CPU detected: {cpu_raw if cpu_raw else 'Unknown'} ({cpu_count} cores)")

    print("[*] Detecting GPU...")
    gpu_info = parse_pci("VGA")
    print(f"    GPU detected: {gpu_info['Manufacturer']} ({gpu_info['Device ID']})")

    print("[*] Detecting Network controller...")
    net_info = parse_pci("Ethernet")
    print(f"    Network detected: {net_info['Device ID']}")

    print("[*] Detecting USB controller...")
    usb_info = parse_pci("USB")
    print(f"    USB controller detected: {usb_info['Device ID']}")

    print("[*] Detecting Storage controller...")
    storage_info = parse_pci("SATA\\|NVMe")
    print(f"    Storage controller detected: {storage_info['Device ID']}")

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
            "Core Count": cpu_count,
            "CPU Count": "1",
            "SIMD Features": "SSE4.2, AVX2"
        },
        "GPU": {
            "Item 0": {
                "Manufacturer": gpu_info["Manufacturer"],
                "Codename": "Unknown",
                "Device ID": gpu_info["Device ID"],
                "Device Type": "Integrated GPU" if gpu_info["Manufacturer"] == "Intel" else "Discrete GPU"
            }
        },
        "Network": {
            "Item 0": {
                "Bus Type": "PCI",
                "Device ID": net_info["Device ID"]
            }
        },
        "USB Controllers": {
            "Item 0": {
                "Bus Type": "PCI",
                "Device ID": usb_info["Device ID"]
            }
        },
        "Input": {
            "Item 0": {"Bus Type": "USB"},
            "Item 1": {"Bus Type": "USB"}
        },
        "Storage Controllers": {
            "Item 0": {
                "Bus Type": "PCI",
                "Device ID": storage_info["Device ID"]
            }
        }
    }

    with open('Report.json', 'w') as f:
        json.dump(report, f, indent=4)

    print("[✓] Report.json generated successfully!")

def open_github():
    print("[*] Opening GitHub page...")
    webbrowser.open(GITHUB_URL)
    print("[✓] GitHub opened in your default browser.")

def menu():
    while True:
        print("\n" + "#"*35)
        print("#        OC-S-ReportGenerator        #")
        print("#"*35)
        print("1. Generate file")
        print("2. Open GitHub")
        print("3. Quit")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            generate_report()
        elif choice == "2":
            open_github()
        elif choice == "3":
            print("Exiting... Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid option. Try again.")

if __name__ == "__main__":
    check_root()
    menu()
