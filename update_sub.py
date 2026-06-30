#!/usr/bin/env python3
import requests
import re
import os
from pathlib import Path

# --- Конфигурация ---
SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
OUTPUT_PATH = "Githubmirorr/Sub/BlankedVPN/sub.txt"

# Сколько конфигов каждого типа нужно взять (берём первые попавшиеся)
LIMIT_VLESS = 3
LIMIT_HYSTERIA = 2

# --- Функции обработки ---

def parse_tag(original_tag: str) -> str:
    """
    Определяет новый тег по правилам на основе содержимого оригинального тега.
    Возвращает строку для подстановки после '#'.
    """
    tag_lower = original_tag.lower()
    if "cidr" in tag_lower:
        return "BlankedVPN | [*CIDR]"
    elif "whitelist" in tag_lower:  # охватывает WhiteList и Whitelist
        return "BlankedVPN | WhiteList 🏳️"
    elif "anycast" in tag_lower:
        return "BlankedVPN | Anycast-IP"
    else:
        # Если не совпало ни одно условие — оставляем оригинальный тег без изменений
        # (но можно и переименовать в нейтральный, решайте сами)
        return original_tag

def process_configs(raw_lines: list[str]):
    """
    Проходит по строкам, собирает vless и hysteria2,
    возвращает список преобразованных строк (каждая - готовая конфигурация).
    """
    vless_found = []
    hysteria_found = []

    # Регулярки для протоколов (с учётом возможных вариантов начала)
    vless_pattern = re.compile(r'^vless://', re.IGNORECASE)
    hy2_pattern = re.compile(r'^(hysteria2://|hy2://)', re.IGNORECASE)

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue

        # Определяем протокол
        if vless_pattern.match(line):
            # Проверяем, что это именно TCP Reality (в строке может быть указание reality)
            # Поскольку источник явно содержит "Vless-Reality", будем считать все vless подходящими
            if len(vless_found) < LIMIT_VLESS:
                vless_found.append(line)
        elif hy2_pattern.match(line):
            if len(hysteria_found) < LIMIT_HYSTERIA:
                hysteria_found.append(line)
        # Другие протоколы игнорируем

        # Если набрали нужное количество обоих типов, можно досрочно прервать (для скорости)
        if len(vless_found) >= LIMIT_VLESS and len(hysteria_found) >= LIMIT_HYSTERIA:
            break

    # Объединяем: сначала VLESS, потом Hysteria2
    selected = vless_found + hysteria_found

    # Теперь меняем теги у каждой выбранной строки
    result = []
    for cfg in selected:
        # Разделяем по символу '#'
        if '#' in cfg:
            base, old_tag = cfg.split('#', 1)
            new_tag = parse_tag(old_tag)
            new_cfg = f"{base}#{new_tag}"
        else:
            # Если тега нет — добавляем стандартный (на всякий случай)
            new_cfg = f"{cfg}#BlankedVPN"
        result.append(new_cfg)

    return result

def main():
    # Скачиваем исходный файл
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return

    # Разбиваем на строки
    raw_lines = resp.text.splitlines()
    processed = process_configs(raw_lines)

    # Формируем содержимое с шапкой
    header = [
        "#profile-title: BlankedVPN",
        "#profile-update-interval: 1",
        "#announce: Если у вас возникли проблемы с работой сервиса - выключите впн и обновите подписку нажав на кнопку 🔄",
        "#subscription-userinfo: upload=0; download=0; total=0; expire=253402214400",
        ""  # пустая строка после шапки
    ]

    full_content = "\n".join(header) + "\n" + "\n".join(processed)

    # Создаём папки, если их нет
    output_file = Path(OUTPUT_PATH)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Записываем
    output_file.write_text(full_content, encoding='utf-8')
    print(f"✅ Файл сохранён: {OUTPUT_PATH}")
    print(f"Всего конфигов: {len(processed)} (VLESS: {len([c for c in processed if c.startswith('vless://')])}, Hysteria2: {len([c for c in processed if c.startswith(('hysteria2://','hy2://'))])})")

if __name__ == "__main__":
    main()
