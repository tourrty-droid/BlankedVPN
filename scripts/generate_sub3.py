#!/usr/bin/env python3
"""
Генератор sub3.txt с 5 случайными VPN конфигами
Обновляется каждые 30 минут через GitHub Actions
"""

import requests
import random
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt"
OUTPUT_FILE = "sub3.txt"
NUM_CONFIGS = 5

def fetch_configs(url):
    """Загружает конфиги из источника"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"✅ Загружено: {len(response.text)} байт")
        return response.text
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None

def parse_configs(content):
    """Разбирает конфиги по пустым строкам"""
    if not content:
        return []
    
    configs = []
    current = []
    
    for line in content.split('\n'):
        if line.strip():
            current.append(line)
        elif current:
            configs.append('\n'.join(current))
            current = []
    
    if current:
        configs.append('\n'.join(current))
    
    return configs

def main():
    print(f"🚀 Генерация sub3.txt [{datetime.now().strftime('%H:%M:%S')}]")
    
    # Загрузка
    content = fetch_configs(SOURCE_URL)
    if not content:
        with open(OUTPUT_FILE, 'w') as f:
            f.write("# Ошибка загрузки\n")
        return
    
    # Парсинг
    configs = parse_configs(content)
    print(f"📊 Найдено конфигов: {len(configs)}")
    
    if not configs:
        with open(OUTPUT_FILE, 'w') as f:
            f.write("# Конфиги не найдены\n")
        return
    
    # Выбор случайных
    selected = random.sample(configs, min(NUM_CONFIGS, len(configs)))
    
    # Формирование файла
    output = f"""# sub3.txt - VPN конфиги для России
# Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Источник: {SOURCE_URL}
# Выбрано: {len(selected)} из {len(configs)}
# ============================================

"""
    output += '\n\n'.join(selected) + '\n'
    
    # Сохранение
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✅ sub3.txt обновлен ({len(selected)} конфигов, {len(output)} байт)")

if __name__ == "__main__":
    main()
