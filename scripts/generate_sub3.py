#!/usr/bin/env python3
"""
Генератор sub3.txt для BlankedVPN
6 случайных конфигов каждые 30 минут
"""

import requests
import random
from datetime import datetime

URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt"
FILE = "sub3.txt"
NUM = 6

def fetch():
    try:
        r = requests.get(URL, timeout=30)
        r.raise_for_status()
        print(f"✅ Загружено: {len(r.text)} байт")
        return r.text
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def parse(text):
    configs = []
    cur = []
    for line in text.split('\n'):
        if line.strip():
            cur.append(line)
        elif cur:
            configs.append('\n'.join(cur))
            cur = []
    if cur:
        configs.append('\n'.join(cur))
    print(f"📊 Конфигов: {len(configs)}")
    return configs

def main():
    print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')}")
    
    raw = fetch()
    if not raw:
        with open(FILE, 'w') as f:
            f.write("# Ошибка загрузки\n")
        return
    
    configs = parse(raw)
    if not configs:
        with open(FILE, 'w') as f:
            f.write("# Нет конфигов\n")
        return
    
    selected = random.sample(configs, min(NUM, len(configs)))
    
    out = f"""# BlankedVPN - sub3.txt 🇷🇺
# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Конфигов: {len(selected)} из {len(configs)}
# Обновление: каждые 30 мин
# ============================================

"""
    out += '\n\n'.join(selected) + '\n'
    
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(out)
    
    print(f"✅ {FILE} создан | {len(out)} байт")

if __name__ == "__main__":
    main()
