import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from marketing_config import CampaignManager


load_dotenv()
TEXT_MODEL = os.getenv("NEWS_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _openai_generate(system_prompt: str, prompt: str, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    if not response.choices:
        return ""
    return (response.choices[0].message.content or "").strip()


class AdCreativeGenerator:
    def __init__(self) -> None:
        self.manager = CampaignManager()

    def generate_ad_drafts(self, topic: str, product_info: str) -> dict[str, Any]:
        if not self.manager.check_safety(topic):
            return {"status": "RESTRICTED_SMM_ONLY", "drafts": []}

        system_prompt = (
            "Ты — рекламный копирайтер. Сгенерируй 3 варианта объявлений "
            "для Яндекс.Директа. Соблюдай ограничения по длине строго."
        )
        prompt = (
            "Тема: "
            f"{topic}\n"
            "Описание продукта:\n"
            f"{product_info}\n\n"
            "Выдай строго JSON-объект без Markdown со структурой:\n"
            "{\n"
            '  "status": "OK",\n'
            '  "drafts": [\n'
            "    {\n"
            '      "title_1": "...",\n'
            '      "title_2": "...",\n'
            '      "text": "...",\n'
            '      "keywords": ["...", "..."]\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Ограничения:\n"
            "- Заголовок 1: максимум 35 символов\n"
            "- Заголовок 2: максимум 30 символов\n"
            "- Текст: максимум 81 символ (включая пробелы)\n"
            "- Ключевые слова: 10-15 запросов на русском\n"
        )
        raw = _openai_generate(system_prompt, prompt, TEXT_MODEL)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "OK", "drafts_raw": raw}


if __name__ == "__main__":
    generator = AdCreativeGenerator()
    sample_info = "Научно обоснованный продукт для поддержки здоровья."

    print("=== BPC-157 ===")
    print(json.dumps(generator.generate_ad_drafts("BPC-157", sample_info), ensure_ascii=False, indent=2))

    print("=== Semaglutide ===")
    print(json.dumps(generator.generate_ad_drafts("Semaglutide", sample_info), ensure_ascii=False, indent=2))
