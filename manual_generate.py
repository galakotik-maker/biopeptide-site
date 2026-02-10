import json
import os
from datetime import datetime

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from research_auto_ai import (
    JOURNAL_ENDPOINT,
    TEXT_MODEL,
    _build_image_prompt,
    _collect_search_snippets,
    _generate_image_url,
    _openai_generate_with_system,
    _send_journal_post,
)


TOPIC = "Биопептиды и долголетие"
QUERIES = [
    "Биопептиды и долголетие Epitalon",
    "Биопептиды и долголетие Thymulin",
]


NEWS_SYSTEM_PROMPT = (
    "Ты — научный редактор BioPeptidePlus. "
    "Пиши на русском, строго по фактам из предоставленного текста. "
    "Никаких выдуманных данных. Если факт отсутствует — не добавляй его. "
    "Верни текст СТРОГО в указанном формате без JSON."
)


def _build_prompt(topic: str, raw_text: str) -> str:
    return (
        f"Тема: {topic}\n\n"
        "Сформируй ОДНУ актуальную новость по теме на основе текста ниже.\n"
        "Верни результат строго в формате:\n"
        "### LITE\n"
        "<короткий пост для Telegram: дружелюбный тон, эмодзи, призыв>\n"
        "### EXPERT\n"
        "<первая строка — заголовок. Далее экспертный текст в формате тегов: вводный текст, > цитата, [СУТЬ], [ПОЛЬЗА] с пунктами, [РЕКОМЕНДАЦИЯ]>\n"
        "### ARTICLE\n"
        "<первая строка — заголовок. Далее развернутый текст в том же формате тегов>\n\n"
        "Текст источника:\n"
        f"{raw_text}\n"
    )


def _parse_sections(raw: str) -> dict:
    sections: dict[str, str] = {"lite": "", "expert": "", "article": ""}
    current = ""
    for line in raw.splitlines():
        normalized = line.strip()
        if normalized.startswith("### LITE"):
            current = "lite"
            continue
        if normalized.startswith("### EXPERT"):
            current = "expert"
            continue
        if normalized.startswith("### ARTICLE"):
            current = "article"
            continue
        if current:
            sections[current] += (line + "\n")
    return {k: v.strip() for k, v in sections.items()}


def _generate_news_item(topic: str, raw_text: str) -> dict:
    prompt = _build_prompt(topic, raw_text)
    raw = ""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if OpenAI and api_key:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        if response.choices:
            raw = (response.choices[0].message.content or "").strip()
    elif api_key:
        safe_key = api_key.encode("latin-1", "ignore").decode("latin-1")
        os.environ["OPENAI_API_KEY"] = safe_key
        raw = _openai_generate_with_system(NEWS_SYSTEM_PROMPT, prompt, TEXT_MODEL)
    else:
        raise ValueError("OpenAI client недоступен или ключ не найден.")
    return _parse_sections(raw)


def _build_payload(news: dict, image_url: str) -> dict:
    lite = str(news.get("lite", "")).strip()
    expert = str(news.get("expert", "")).strip()
    article = str(news.get("article", "")).strip()
    title = ""
    for line in (expert or article).splitlines():
        if line.strip():
            title = line.strip()
            break
    if not title or not lite or not expert or not article:
        raise ValueError("Пустые поля в сгенерированном тексте.")

    content = article
    return {
        "title": title,
        "content": content,
        "content_lite": lite,
        "category": "science",
        "is_published": True,
        "image_url": image_url,
        "generated_at": datetime.utcnow().isoformat(),
        "source": TOPIC,
    }


def publish_to_supabase(payload: dict) -> dict:
    return _send_journal_post(payload)


def main() -> None:
    load_dotenv()
    print(f"JOURNAL_ENDPOINT: {JOURNAL_ENDPOINT}")
    published = 0

    for query in QUERIES:
        snippets = _collect_search_snippets(query, max_results=6)
        if not snippets:
            print(f"Нет данных по запросу: {query}")
            continue

        news = _generate_news_item(TOPIC, snippets)
        if not news:
            print(f"Пустой ответ для: {query}")
            continue

        title = str(news.get("title", "")).strip()
        if not title:
            for line in (news.get("expert", "") or news.get("article", "")).splitlines():
                if line.strip():
                    title = line.strip()
                    break
        image_prompt = _build_image_prompt(title or TOPIC)
        image_url = _generate_image_url(image_prompt) or ""
        if not image_url:
            raise ValueError("Image generation failed: image_url is empty.")
        payload = _build_payload(news, image_url)
        response = publish_to_supabase(payload)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        published += 1

    print(f"Готово. Опубликовано новостей: {published}")


if __name__ == "__main__":
    main()
