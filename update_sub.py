#!/usr/bin/env python3
import requests
import re
import os
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
OUTPUT_PATH = "Githubmirorr/Sub/BlankedVPN/sub.txt"
LIMIT_VLESS = 3
LIMIT_HYSTERIA = 2

def is_valid_vless(line):
    if not line.startswith("vless://"):
        return False
    lower = line.lower()
    if "security=reality" not in lower:
        return False
    if "network=tcp" not in lower and "type=tcp" not in lower:
        return False
    return True

def parse_tag(original_tag):
    tag_lower = original_tag.lower()
    if "cidr" in tag_lower:
        return "BlankedVPN | [*CIDR]"
    elif "whitelist" in tag_lower:
        return "BlankedVPN | WhiteList 🏳️"
    elif "anycast" in tag_lower:
        return "BlankedVPN | Anycast-IP"
    else:
        return original_tag

def process_configs(raw_lines):
    vless_found = []
    hysteria_found = []
    hy2_pattern = re.compile(r'^(hysteria2://|hy2://)', re.IGNORECASE)
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("vless://") and is_valid_vless(line):
            if len(vless_found) < LIMIT_VLESS:
                vless_found.append(line)
        elif hy2_pattern.match(line):
            if len(hysteria_found) < LIMIT_HYSTERIA:
                hysteria_found.append(line)
        if len(vless_found) >= LIMIT_VLESS and len(hysteria_found) >= LIMIT_HYSTERIA:
            break
    selected = vless_found + hysteria_found
    result = []
    for cfg in selected:
        if '#' in cfg:
            base, old_tag = cfg.split('#', 1)
            new_tag = parse_tag(old_tag)
            new_cfg = f"{base}#{new_tag}"
        else:
            new_cfg = f"{cfg}#BlankedVPN"
        result.append(new_cfg)
    return result

def main():
    print("Downloading source...")
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error: {e}")
        return
    raw_lines = resp.text.splitlines()
    processed = process_configs(raw_lines)
    header = [
        "#profile-title: BlankedVPN",
        "#profile-update-interval: 1",
        "#announce: If you have problems, disable VPN and update subscription by pressing 🔄",
        "#subscription-userinfo: upload=0; download=0; total=0; expire=253402214400",
        ""
    ]
    full_content = "\n".join(header) + "\n" + "\n".join(processed)
    output_file = Path(OUTPUT_PATH)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(full_content, encoding='utf-8')
    print(f"Saved to {OUTPUT_PATH}")
    vless_count = sum(1 for c in processed if c.startswith('vless://'))
    hy2_count = sum(1 for c in processed if c.startswith(('hysteria2://','hy2://')))
    print(f"Counts: VLESS={vless_count}, Hysteria2={hy2_count}")

if __name__ == "__main__":
    main()
