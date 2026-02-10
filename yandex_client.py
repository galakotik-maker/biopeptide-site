import json
import os
from typing import Optional

import requests
from dotenv import load_dotenv


class YandexDirectClient:
    def __init__(self) -> None:
        load_dotenv()
        self.token = os.getenv("YANDEX_TOKEN", "").strip()
        self.login = os.getenv("YANDEX_LOGIN", "").strip()
        self.base_url = "https://api.direct.yandex.com/json/v5/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Client-Login": self.login,
            "Accept-Language": "ru",
            "Content-Type": "application/json",
        }

    def get_campaigns_list(self) -> Optional[list[dict]]:
        payload = {
            "method": "get",
            "params": {"FieldNames": ["Id", "Name", "State"]},
        }
        try:
            response = requests.post(
                f"{self.base_url}campaigns",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30,
            )
        except requests.RequestException as exc:
            print(f"Ошибка запроса: {exc}")
            return None

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code} {response.text}")
            return None

        data = response.json()
        return data.get("result", {}).get("Campaigns", []) or []

    def create_test_campaign(self, name: str, weekly_budget_amount: float) -> Optional[int]:
        payload = {
            "method": "add",
            "params": {
                "Campaigns": [
                    {
                        "Name": name,
                        "TextCampaign": {
                            "BiddingStrategy": {
                                "Search": {"BiddingStrategyType": "WB_MAXIMUM_CLICKS"},
                                "Network": {"BiddingStrategyType": "WB_MAXIMUM_CLICKS"},
                            }
                        },
                        "Strategy": {"WeeklyBudget": {"Amount": weekly_budget_amount}},
                    }
                ]
            },
        }
        try:
            response = requests.post(
                f"{self.base_url}campaigns",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30,
            )
        except requests.RequestException as exc:
            print(f"Ошибка запроса: {exc}")
            return None

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code} {response.text}")
            return None

        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))

        add_results = (response_data.get("result") or {}).get("AddResults") or []
        if not add_results:
            print("Ошибка: пустой ответ AddResults.")
            return None

        first_result = add_results[0] or {}
        errors = first_result.get("Errors") or []
        if errors:
            print("Ошибки при создании кампании:")
            for err in errors:
                code = err.get("Code")
                message = err.get("Message")
                details = err.get("Details")
                print(f"- Code: {code} | Message: {message} | Details: {details}")
            return None

        campaign_id = first_result.get("Id")
        if not campaign_id:
            print("Ошибка: ID кампании не найден в ответе.")
            return None

        return campaign_id


if __name__ == "__main__":
    client = YandexDirectClient()
    campaigns = client.get_campaigns_list()
    if campaigns is None:
        print("Связи нет. Проверь YANDEX_TOKEN и YANDEX_LOGIN.")
    else:
        print(f"Связь есть! Найдено кампаний: {len(campaigns)}")
        new_campaign_id = client.create_test_campaign("AI_TEST_BPC157", 5000)
        if new_campaign_id:
            print(f"Кампания создана! ID: {new_campaign_id}")
        else:
            print("Не удалось создать кампанию.")
