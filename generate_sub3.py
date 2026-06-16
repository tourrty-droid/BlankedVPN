import requests
import random
from datetime import datetime

URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt"
FILE = "BlankedVPN/sub3.txt"

try:
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    print(f"✅ Loaded: {len(r.text)} bytes")
    
    configs, cur = [], []
    for line in r.text.split('\n'):
        if line.strip():
            cur.append(line)
        elif cur:
            configs.append('\n'.join(cur))
            cur = []
    if cur:
        configs.append('\n'.join(cur))
    
    print(f"📊 Configs: {len(configs)}")
    
    selected = random.sample(configs, min(6, len(configs)))
    
    out = f"# BlankedVPN 🇷🇺\n# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n# Configs: {len(selected)}/{len(configs)}\n\n"
    out += '\n\n'.join(selected)
    
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(out)
    
    print(f"✅ {FILE} created | {len(out)} bytes | {len(selected)} configs")

except Exception as e:
    print(f"❌ Error: {e}")
    with open(FILE, 'w') as f:
        f.write("# Error loading configs\n")
