import os
import json
import urllib.request

from dotenv import load_dotenv

import comment_handler


def check_research_db() -> bool:
    db_path = comment_handler.DB_PATH
    if not os.path.isdir(db_path):
        return False
    required = {"tirzepatide.txt", "bpc157.txt"}
    existing = set(os.listdir(db_path))
    return required.issubset(existing)


def check_mapping() -> bool:
    try:
        response = comment_handler.get_peptide_info("тирзепатид")
    except Exception:
        return False
    return "В моей базе пока нет данных" not in response


def check_telegram() -> bool:
    token = os.getenv("ARBITER_TOKEN")
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/getMe"
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return bool(payload.get("ok"))
    except Exception:
        return False


def check_moderation() -> bool:
    try:
        return comment_handler._is_violation("http://test.com")
    except Exception:
        return False


def main() -> None:
    load_dotenv()

    db_ok = check_research_db()
    mapping_ok = check_mapping()
    telegram_ok = check_telegram()
    moderation_ok = check_moderation()

    print(f"База данных: {'OK' if db_ok else 'FAIL'}")
    print(f"Поиск пептидов: {'OK' if mapping_ok else 'FAIL'}")
    print(f"Связь с Telegram: {'OK' if telegram_ok else 'FAIL'}")
    print(f"Модерация: {'OK' if moderation_ok else 'FAIL'}")


if __name__ == "__main__":
    main()
