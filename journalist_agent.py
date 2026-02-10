import json
import os
import re
import shutil
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


BP_PLUS_PROMPT = """Ты — Ведущий научный обозреватель BioPeptidePlus. Твоя задача — писать премиальный контент для вкладки 'BP+ View'.

Тон: Экспертный, дорогой ('Quiet Luxury'), метафоричный. Ты объясняешь сложные биохимические процессы (теломеры, экспрессия генов) через понятные образы (архитектура, ключи, ремонт).

СТРОГОЕ ТРЕБОВАНИЕ К ФОРМАТУ:
Используй ТОЛЬКО следующие маркеры (ровно в таком виде):

### TITLE: <Текст заголовка>
### QUOTE: <Текст цитаты>
### ESSENCE: <Текст сути>
### BENEFITS: (далее список через 🔸)
### RECOMMENDATION: <Текст рекомендации>

Остальное (вступление, детали, научный контекст) пиши обычным текстом между блоками.
Список BENEFITS обязательно 3-4 пункта, каждый начинается с символа 🔸."""

DATA_FILE_PATH = os.path.join(
    os.getcwd(),
    "legal-guard-regtech-master",
    "frontend",
    "src",
    "data",
    "journalData.ts",
)


def _generate_with_openai(prompt: str, user_input: str) -> Optional[str]:
    if OpenAI is None:
        return None

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("NEWS_MODEL", "gpt-4o-mini"),
        temperature=0.6,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
    )
    if not response.choices:
        return None
    return (response.choices[0].message.content or "").strip()


def create_draft(topic: str, raw_data: str) -> str:
    user_input = (
        f"Тема: {topic}\n\n"
        f"Сырой текст исследования:\n{raw_data}\n\n"
        "Сформируй итоговый текст строго по структуре."
    )
    generated = _generate_with_openai(BP_PLUS_PROMPT, user_input)
    if generated:
        return generated

    # Fallback if OpenAI key is missing.
    sentences = [part.strip() for part in re.split(r"[.!?]\s+", raw_data) if part.strip()]
    quote = sentences[0] if sentences else raw_data.strip()
    essence = sentences[1] if len(sentences) > 1 else raw_data.strip()
    title = topic.strip() or "Новый обзор BioPeptidePlus"
    benefits = [
        "Поддержка ключевых биоритмов иммунитета",
        "Усиление регенеративного ответа тканей",
        "Стабилизация адаптивной реакции организма",
    ]
    recommendation = (
        "Команда BioPeptidePlus рекомендует индивидуальную схему под цели и статус клиента. "
        "Запросите консультацию для точного протокола."
    )
    return (
        f"### TITLE: {title}\n\n"
        f"{raw_data.strip()}\n\n"
        f"### QUOTE: {quote}\n\n"
        f"### ESSENCE: {essence}\n\n"
        "### BENEFITS:\n"
        + "\n".join(f"🔸 {item}" for item in benefits)
        + "\n\n"
        f"### RECOMMENDATION: {recommendation}"
    )


def save_post(content: str, filename: str) -> str:
    output_dir = os.path.join(os.getcwd(), "content_queue")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = filename.strip() or "bp_plus_post.md"
    if not safe_name.endswith(".md"):
        safe_name += ".md"
    path = os.path.join(output_dir, safe_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _extract_title(text: str) -> str:
    match = re.search(r"^###\s*TITLE:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_quote(text: str) -> str:
    match = re.search(r"^###\s*QUOTE:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_essence(text: str) -> str:
    match = re.search(r"^###\s*ESSENCE:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_benefits(text: str) -> list[str]:
    match = re.search(
        r"^###\s*BENEFITS:\s*(.*?)(?=^###\s*RECOMMENDATION:|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    block = match.group(1).strip()
    raw_items = re.split(r"🔸", block)
    items = [item.strip(" -\n\t\r") for item in raw_items if item.strip(" -\n\t\r")]
    return items


def _extract_recommendation(text: str) -> str:
    match = re.search(r"^###\s*RECOMMENDATION:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _build_description(title: str, intro: str, quote: str, essence: str, benefits: list[str], recommendation: str) -> str:
    parts = []
    if title:
        parts.append(f"## {title}")
    if intro:
        parts.append(intro)
    if quote:
        parts.append(f"> {quote}")
    if essence:
        parts.append("## Суть")
        parts.append(essence)
    if benefits:
        parts.append("## Польза")
        parts.append("\n".join(f"- {item}" for item in benefits))
    if recommendation:
        parts.append("## Рекомендация")
        parts.append(recommendation)
    return "\n\n".join(parts).strip()


def parse_markdown_to_article(content: str) -> dict:
    title = _extract_title(content)
    quote = _extract_quote(content)
    essence = _extract_essence(content)
    benefits = _extract_benefits(content)
    recommendation = _extract_recommendation(content)
    date_value = datetime.now().strftime("%Y-%m-%d")
    expert_view = essence or "Краткий разбор механизма и ключевых эффектов."
    lite_view = f"{title}. {benefits[0]}" if title and benefits else "Короткая выжимка для быстрого чтения."
    description = _build_description(title, "", quote, essence, benefits, recommendation)

    return {
        "id": f"bpplus-{int(datetime.now().timestamp())}",
        "title": title,
        "quote": quote,
        "essence": essence,
        "benefits": benefits,
        "recommendation": recommendation,
        "date": date_value,
        "expert_view": expert_view,
        "lite_view": lite_view,
        "description": description,
    }


def _ensure_data_file() -> None:
    if os.path.exists(DATA_FILE_PATH):
        return
    os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
    template = (
        "export type JournalArticle = {\n"
        "  id: string\n"
        "  title: string\n"
        "  quote: string\n"
        "  essence: string\n"
        "  benefits: string[]\n"
        "  recommendation: string\n"
        "  date: string\n"
        "  expert_view: string\n"
        "  lite_view: string\n"
        "  description: string\n"
        "}\n\n"
        "export const journalData: JournalArticle[] = [\n"
        "]\n"
    )
    with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(template)


def publish_to_site(article_object: dict) -> str:
    _ensure_data_file()
    backup_path = DATA_FILE_PATH + ".bak"
    shutil.copyfile(DATA_FILE_PATH, backup_path)

    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "export const journalData: JournalArticle[] = ["
    if marker not in content:
        raise ValueError("Не найден массив journalData в файле.")

    insert_pos = content.find(marker) + len(marker)
    article_json = json.dumps(article_object, ensure_ascii=False, indent=2)
    indented = "\n".join(f"  {line}" if line.strip() else line for line in article_json.splitlines())
    new_content = content[:insert_pos] + "\n" + indented + ",\n" + content[insert_pos:]

    with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    return DATA_FILE_PATH


def main() -> None:
    load_dotenv()
    topic = "Пептиды для иммунитета"
    raw_data = (
        "Тималин — пептидный биорегулятор тимуса. "
        "В исследованиях отмечали нормализацию Т-клеточного звена "
        "и повышение резистентности у пациентов с иммунодефицитными состояниями."
    )
    content = create_draft(topic, raw_data)
    saved_path = save_post(content, "bp_plus_immunity")
    print(f"Готово. Файл сохранен: {saved_path}")
    article_object = parse_markdown_to_article(content)
    data_path = publish_to_site(article_object)
    print(f"Статья добавлена в данные сайта: {data_path}")


if __name__ == "__main__":
    main()
