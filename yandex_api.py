import os
import json
import requests
from dotenv import load_dotenv

# Загружаем настройки
load_dotenv()

TOKEN = os.getenv("YANDEX_TOKEN")
LOGIN = os.getenv("YANDEX_LOGIN")
CAMPAIGN_ID = os.getenv("CAMPAIGN_ID")

class YandexClient:
    def __init__(self):
        self.base_url = "https://api.direct.yandex.com/json/v5/"
        self.headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Client-Login": LOGIN,
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8"
        }

    def check_connection(self):
        print(f"📡 Проверяем связь с кампанией ID: {CAMPAIGN_ID}...")
        
        body = {
            "method": "get",
            "params": {
                "SelectionCriteria": {"Ids": [CAMPAIGN_ID]},
                "FieldNames": ["Id", "Name", "State", "Status", "Funds"] 
            }
        }
        
        try:
            response = requests.post(
                self.base_url + "campaigns", 
                headers=self.headers, 
                data=json.dumps(body)
            )
            
            # Если Яндекс ответил (даже с ошибкой)
            data = response.json()
            
            if "error" in data:
                print(f"❌ Ошибка API: {data['error']['error_string']}")
                print(f"Детали: {data['error']['description']}")
            elif "result" in data and data["result"]["Campaigns"]:
                camp = data["result"]["Campaigns"][0]
                print("\n✅ УСПЕХ! Мы видим кампанию:")
                print(f"--- Название: {camp['Name']}")
                print(f"--- Состояние: {camp['State']} (Status: {camp['Status']})")
                print("--- Связь установлена. Агент готов к работе.")
            else:
                print("⚠️ Кампания не найдена. Проверь ID.")
                print(data)

        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    if not TOKEN or not LOGIN:
        print("❌ Ошибка: В файле .env не заполнен Токен или Логин!")
    else:
        client = YandexClient()
        client.check_connection()

        