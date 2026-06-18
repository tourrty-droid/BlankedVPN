import requests
import re
import urllib.parse
import time
from collections import OrderedDict

# ------------------- Настройки -------------------
OUTPUT_FILE = "Githubmirorr/Sub/BlankedVPN/sub8.txt"
SOURCES = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/27.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/26.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/30.txt",
]
MAX_CONFIGS = 100  # брать не более 100 конфигураций

# Заголовок (шапка) для файла подписки
HEADER = """#profile-title: BlankedVPN
#profile-update-interval: 1
#announce: Если у вас возникли проблемы с работой сервиса - выключите впн и обновите подписку нажав на кнопку 🔄
#subscription-userinfo: upload=0; download=0; total=0; expire=253402214400

"""

# Карта кодов стран → флаги (Unicode)
FLAG_MAP = {
    'RU': '🇷🇺', 'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
    'CA': '🇨🇦', 'AU': '🇦🇺', 'JP': '🇯🇵', 'CN': '🇨🇳', 'HK': '🇭🇰',
    'SG': '🇸🇬', 'NL': '🇳🇱', 'PL': '🇵🇱', 'UA': '🇺🇦', 'IN': '🇮🇳',
    'BR': '🇧🇷', 'MX': '🇲🇽', 'IT': '🇮🇹', 'ES': '🇪🇸', 'SE': '🇸🇪',
    'NO': '🇳🇴', 'FI': '🇫🇮', 'DK': '🇩🇰', 'BE': '🇧🇪', 'CH': '🇨🇭',
    'AT': '🇦🇹', 'CZ': '🇨🇿', 'GR': '🇬🇷', 'PT': '🇵🇹', 'IE': '🇮🇪',
    'NZ': '🇳🇿', 'ZA': '🇿🇦', 'AE': '🇦🇪', 'SA': '🇸🇦', 'IL': '🇮🇱',
    'TR': '🇹🇷', 'PK': '🇵🇰', 'BD': '🇧🇩', 'VN': '🇻🇳', 'TH': '🇹🇭',
    'MY': '🇲🇾', 'ID': '🇮🇩', 'PH': '🇵🇭', 'EG': '🇪🇬', 'NG': '🇳🇬',
}

# Кэш для стран (чтобы не дёргать API повторно)
country_cache = {}

def get_country_info(host):
    """Определяет страну по IP/хосту через ip-api.com"""
    if host in country_cache:
        return country_cache[host]
    try:
        # ip-api.com принимает как IP, так и домен
        url = f"http://ip-api.com/json/{host}?fields=country,countryCode"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                code = data.get('countryCode', '')
                country_cache[host] = (country, code)
                return country, code
    except Exception:
        pass
    country_cache[host] = ('Unknown', '')
    return 'Unknown', ''

def get_flag(country_code):
    """Возвращает эмодзи флага по коду страны"""
    return FLAG_MAP.get(country_code.upper(), '🏳️')

def extract_vless_links(text):
    """Извлекает все строки, начинающиеся с vless://"""
    return re.findall(r'vless://[^\s]+', text)

def process_vless_line(line):
    """
    Обрабатывает одну VLESS-строку:
    - извлекает хост (сервер)
    - определяет страну
    - заменяет/добавляет #название на "🇷🇺 Russia" (пример)
    """
    # Разбиваем URL
    # Формат: vless://uuid@host:port?params#name
    # Или без #name
    parsed = urllib.parse.urlparse(line)
    if not parsed.netloc:
        # Если не удалось распарсить, возвращаем как есть
        return line

    # Извлекаем хост (может быть IP или домен)
    # netloc имеет вид host:port или host
    host = parsed.netloc.split(':')[0] if ':' in parsed.netloc else parsed.netloc

    # Определяем страну
    country, code = get_country_info(host)
    flag = get_flag(code)
    # Формируем новое название
    new_name = f"{flag} {country}".strip()
    if not new_name:
        new_name = "Unknown"

    # Если есть fragment (#name), заменяем его
    if parsed.fragment:
        # Удаляем старый fragment и добавляем новый
        new_line = line.rsplit('#', 1)[0] + '#' + new_name
    else:
        new_line = line + '#' + new_name

    return new_line

def main():
    # 1. Скачиваем все файлы
    all_text = ""
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                all_text += resp.text + "\n"
            else:
                print(f"Failed to download {url}, status {resp.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    # 2. Извлекаем VLESS
    raw_links = extract_vless_links(all_text)
    print(f"Found {len(raw_links)} VLESS links")

    # 3. Ограничиваем количество
    if len(raw_links) > MAX_CONFIGS:
        raw_links = raw_links[:MAX_CONFIGS]
        print(f"Truncated to {MAX_CONFIGS}")

    # 4. Обрабатываем каждую строку (добавляем флаги)
    processed = []
    for idx, link in enumerate(raw_links):
        try:
            new_link = process_vless_line(link)
            processed.append(new_link)
        except Exception as e:
            print(f"Error processing link {idx}: {e}")
            processed.append(link)  # оставляем как есть
        # Небольшая задержка, чтобы не перегружать API
        time.sleep(0.2)

    # 5. Формируем итоговое содержимое
    content = HEADER + "\n".join(processed)

    # 6. Записываем в файл (создаём папки, если надо)
    import os
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Saved {len(processed)} configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
