import json
import os
import time
from datetime import datetime
from typing import Optional

import requests

from yandex_api import YandexClient


DEFAULT_CAMPAIGN_ID = "707134038"
REPORT_PATH = os.path.join(os.getcwd(), "daily_report.txt")


def _parse_report_tsv(tsv_text: str) -> Optional[tuple[int, float]]:
    lines = [line for line in tsv_text.splitlines() if line.strip()]
    if not lines:
        return None

    # Find header line with required fields.
    header_idx = None
    for idx, line in enumerate(lines):
        if "CampaignId" in line and "Clicks" in line and "Cost" in line:
            header_idx = idx
            break

    if header_idx is None or header_idx + 1 >= len(lines):
        return None

    data_lines = lines[header_idx + 1 :]
    for line in data_lines:
        if line.startswith("Total"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        clicks_raw = parts[1].strip()
        cost_raw = parts[2].strip().replace(",", ".")
        try:
            clicks = int(float(clicks_raw))
            cost = float(cost_raw)
            return clicks, cost
        except ValueError:
            continue
    return None


def get_stats(campaign_id: str = DEFAULT_CAMPAIGN_ID) -> Optional[dict]:
    client = YandexClient()
    report_url = f"{client.base_url}reports"
    headers = dict(client.headers)
    headers["processingMode"] = "auto"
    headers["returnMoneyInMicros"] = "false"

    body = {
        "ReportName": "Daily campaign stats",
        "DateRangeType": "TODAY",
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "FieldNames": ["CampaignId", "Clicks", "Cost"],
        "SelectionCriteria": {"CampaignIds": [int(campaign_id)]},
        "Format": "TSV",
        "IncludeVAT": "YES",
        "IncludeDiscount": "NO",
    }

    try:
        response = requests.post(report_url, headers=headers, data=json.dumps(body), timeout=30)
    except requests.RequestException as exc:
        print(f"Ошибка запроса отчета: {exc}")
        return None

    if response.status_code != 200:
        try:
            data = response.json()
            if "error" in data:
                print(f"Ошибка API: {data['error'].get('error_string')}")
                print(f"Детали: {data['error'].get('error_detail')}")
            else:
                print(f"Ошибка API: {response.status_code} {response.text}")
        except ValueError:
            print(f"Ошибка API: {response.status_code} {response.text}")
        return None

    parsed = _parse_report_tsv(response.text)
    if not parsed:
        print("Не удалось распарсить отчет.")
        return None

    clicks, cost = parsed
    return {"campaign_id": campaign_id, "clicks": clicks, "cost": cost}


def check_conversions() -> None:
    # TODO: integrate Yandex Metrika (counter ID: 106548895).
    pass


def _write_report_line(message: str) -> None:
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def run_once(campaign_id: str) -> None:
    stats = get_stats(campaign_id)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not stats:
        _write_report_line(f"[{timestamp}] ERROR: stats unavailable")
        return

    clicks = stats["clicks"]
    cost = stats["cost"]
    cpc = (cost / clicks) if clicks > 0 else 0.0
    line = f"[{timestamp}] campaign={campaign_id} clicks={clicks} cost={cost:.2f} cpc={cpc:.2f}"
    _write_report_line(line)

    if cpc > 60:
        warning = f"[{timestamp}] Внимание! Дорогие клики"
        print(warning)
        _write_report_line(warning)


def main() -> None:
    campaign_id = os.getenv("CAMPAIGN_ID", DEFAULT_CAMPAIGN_ID)
    while True:
        run_once(campaign_id)
        check_conversions()
        time.sleep(3600)


if __name__ == "__main__":
    main()
import os

def save_post_to_file(content, filename="pending_post.md"):
    """
    Сохраняет готовую статью в папку 'content_queue', чтобы Руслан мог её проверить.
    """
    directory = "content_queue"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Статья успешно сохранена в: {filepath}")
    print("🔔 Отправляю уведомление в Telegram: 'Руслан, новая статья готова к проверке!'") 
    # (Сюда позже подключим реальную отправку в телеграм)
    