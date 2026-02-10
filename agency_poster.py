import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


QUERY = "Peptides Longevity Biohacking"
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
)


def _fetch_url(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _parse_pub_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z")
    except Exception:
        return datetime.min


def _get_latest_news() -> dict:
    url = GOOGLE_NEWS_RSS.format(query=urllib.parse.quote_plus(QUERY))
    xml_text = _fetch_url(url)
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("No channel found in RSS feed.")

    items = channel.findall("item")
    if not items:
        raise RuntimeError("No news items found.")

    latest = None
    latest_date = datetime.min
    for item in items:
        pub_date = item.findtext("pubDate", default="")
        dt = _parse_pub_date(pub_date)
        if dt > latest_date:
            latest_date = dt
            latest = item

    if latest is None:
        raise RuntimeError("No latest item found.")

    title = latest.findtext("title", default="").strip()
    link = latest.findtext("link", default="").strip()
    description = latest.findtext("description", default="").strip()
    source = latest.findtext("source", default="").strip()
    return {
        "title": title,
        "link": link,
        "description": description,
        "source": source,
        "published_at": latest_date.isoformat() if latest_date else "",
    }


def _openai_generate(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — научный редактор. Пиши кратко, по делу, по-русски."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        if body:
            print(body)
        raise
    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return ""
    return (choices[0].get("message") or {}).get("content", "").strip()


def _openai_generate_image(title: str, api_key: str) -> Optional[str]:
    prompt = (
        "High-tech biology illustration inspired by: "
        f"{title}. "
        "Style: scientific premium, clean lines, futuristic, laboratory-grade. "
        "Color palette: white, steel, deep blue, cold tones. "
        "No people, no faces, no text."
    )
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "response_format": "url",
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        if body:
            print(body)
        raise
    parsed = json.loads(body)
    items = parsed.get("data", [])
    if not items:
        print("OpenAI image: пустой ответ.")
        return None
    url = items[0].get("url")
    if not url:
        print("OpenAI image: url не получен.")
    return url


def _gemini_generate(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    request = urllib.request.Request(endpoint, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        if body:
            print(body)
        raise
    parsed = json.loads(body)
    candidates = parsed.get("candidates", [])
    if not candidates:
        return ""
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        return ""
    return parts[0].get("text", "").strip()


def _safe_filename(value: str) -> str:
    cleaned = []
    for ch in value.lower():
        if ch.isalnum() or ch in ("-", "_"):
            cleaned.append(ch)
        elif ch.isspace():
            cleaned.append("-")
    name = "".join(cleaned).strip("-")
    return name[:80] if name else "news"


def _split_variants(text: str) -> tuple[str, str]:
    if "===POST===" in text and "===SCIENCE===" in text:
        post = text.split("===POST===", 1)[1].split("===SCIENCE===", 1)[0].strip()
        science = text.split("===SCIENCE===", 1)[1].strip()
        return post, science
    return text.strip(), ""


def _generate_posts(article: dict) -> tuple[str, str]:
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = os.getenv("NEWS_MODEL", "gpt-4o-mini")

    prompt = (
        "Сформируй два текста для Telegram на основе новости.\n"
        f"Заголовок: {article['title']}\n"
        f"Источник: {article['source']}\n"
        f"Ссылка: {article['link']}\n"
        f"Краткое описание: {article['description']}\n\n"
        "Формат ответа строго:\n"
        "===POST===\n"
        "Заголовок:\n"
        "Суть (эмоционально, с пользой для подписчика):\n"
        "Почему это важно (и призыв обсудить):\n"
        "Хэштеги: #BioPeptidePlus #Долголетие\n"
        "===SCIENCE===\n"
        "Научный вариант (сухие факты). "
        "Если в источнике нет дозировок, напиши: "
        "\"Данные в источнике отсутствуют\". "
        "Обязательно укажи ссылку.\n"
    )

    if openai_key:
        try:
            raw = _openai_generate(prompt, openai_key, model)
            return _split_variants(raw)
        except urllib.error.HTTPError:
            pass
    if gemini_key:
        try:
            raw = _gemini_generate(prompt, gemini_key, "gemini-flash-latest")
            return _split_variants(raw)
        except urllib.error.HTTPError:
            pass

    # Fallback без LLM
    title = article["title"] or "Новая статья"
    summary = article["description"] or "Данные в источнике отсутствуют."
    post_text = (
        f"{title}\n"
        f"Суть: {summary}\n"
        "Почему это важно: Данные в источнике отсутствуют.\n"
        "#BioPeptidePlus #Долголетие"
    )
    science_text = (
        f"Заголовок: {title}\n"
        f"Факты: {summary}\n"
        "Дозировки: Данные в источнике отсутствуют.\n"
        f"Ссылка: {article['link']}"
    )
    return post_text, science_text


def _send_telegram(
    text: str, photo_url: Optional[str] = None, link: Optional[str] = None
) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHANNEL_ID") or os.getenv("TELEGRAM_CHANNEL_ID")

    # Если есть фото, используем sendPhoto, если нет — sendMessage
    method = "sendPhoto" if photo_url else "sendMessage"
    telegram_api_url = f"https://api.telegram.org/bot{token}/{method}"

    payload = {"chat_id": chat_id}
    if photo_url:
        payload["photo"] = photo_url
        payload["caption"] = text  # В методе sendPhoto текст идет в caption
    else:
        payload["text"] = text

    if link:
        payload["reply_markup"] = json.dumps(
            {"inline_keyboard": [[{"text": "Источник", "url": link}]]}
        )

    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(telegram_api_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    urllib.request.urlopen(request, timeout=30)


def test_run() -> None:
    article = _get_latest_news()
    post_text, science_text = _generate_posts(article)

    # Генерируем картинку на основе заголовка статьи
    openai_key = os.getenv("OPENAI_API_KEY")
    photo_url = None
    if openai_key:
        try:
            photo_url = _openai_generate_image(article["title"], openai_key)
        except Exception as e:
            print(f"Ошибка генерации фото: {e}")

    # Отправляем пост с фото
    _send_telegram(post_text, photo_url, article.get("link"))
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_db")
    os.makedirs(db_dir, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{_safe_filename(article.get('title', 'news'))}_{stamp}.txt"
    file_path = os.path.join(db_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(science_text.strip() + "\n")
    print("Test Run: пост отправлен.")


if __name__ == "__main__":
    test_run()
