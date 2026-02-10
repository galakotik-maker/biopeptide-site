from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from supabase_client import get_supabase_client, load_env


DEFAULT_MATCH_FN = "match_documents"
EMBEDDING_MODEL = "text-embedding-3-small"


def _telegram_request(token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _openai_embed(text: str) -> list[float]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY for vector search.")
    payload = {"model": EMBEDDING_MODEL, "input": text}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/embeddings", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    return parsed["data"][0]["embedding"]


def _vector_search(query: str, limit: int = 3) -> list[dict]:
    match_fn = os.getenv("SUPABASE_MATCH_FN", DEFAULT_MATCH_FN)
    embedding = _openai_embed(query)
    supabase = get_supabase_client()
    try:
        response = supabase.rpc(
            match_fn,
            {
                "query_embedding": embedding,
                "match_count": limit,
                "match_threshold": 0.0,
            },
        ).execute()
    except Exception:
        return []
    if getattr(response, "error", None):
        return []
    return response.data or []


def _text_search(query: str, limit: int = 5) -> list[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.table("news_articles")
        .select("id,title,url,content,summary,created_at")
        .or_(f"title.ilike.%{query}%,content.ilike.%{query}%,summary.ilike.%{query}%")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    return response.data or []


def _latest_article() -> dict | None:
    supabase = get_supabase_client()
    response = (
        supabase.table("news_articles")
        .select("id,title,url,content,summary,created_at")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    items = response.data or []
    return items[0] if items else None


def _find_best_article(query: str) -> dict | None:
    try:
        vector_hits = _vector_search(query, limit=3)
    except Exception:
        vector_hits = []
    if vector_hits:
        return vector_hits[0]
    hits = _text_search(query, limit=5)
    if hits:
        return hits[0]
    return _latest_article()


def _is_dosage_question(text: str) -> bool:
    keywords = [
        "dose",
        "dosage",
        "how much",
        "мг",
        "мкг",
        "доз",
        "схема",
        "прием",
    ]
    lower = text.lower()
    return any(key in lower for key in keywords)


def _contradiction_needed(text: str, source_url: str) -> bool:
    lower = text.lower()
    if "pubmed" not in source_url.lower() and "nature.com" not in source_url.lower():
        return False
    negation = any(term in lower for term in ("не работает", "неэффектив", "бесполез"))
    return negation


def _compose_answer(query: str, article: dict) -> str:
    title = str(article.get("title", "")).strip()
    url = str(article.get("url", "")).strip()
    summary = str(article.get("summary") or article.get("content") or "").strip()

    if _is_dosage_question(query):
        body = (
            "Обратитесь к Доктору Дрэгу за назначением. "
            "Моя задача — предоставить научную аргументацию."
        )
    else:
        if _contradiction_needed(query, url):
            body = "Утверждение противоречит данным из источника."
        elif summary:
            body = summary
        else:
            body = "В базе нет расширенного описания. Доступна только ссылка."

    citation = f"Источник: {title} — {url}"
    return f"{body}\n\n{citation}".strip()


def _handle_update(token: str, update: dict, allowed_chat_ids: set[str] | None) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return
    chat = message.get("chat", {})
    chat_id = str(chat.get("id"))
    if allowed_chat_ids is not None and chat_id not in allowed_chat_ids:
        return
    text = message.get("text")
    if not text:
        return

    article = _find_best_article(text)
    if not article:
        return
    reply_text = _compose_answer(text, article)

    payload = {
        "chat_id": chat_id,
        "text": reply_text,
        "reply_to_message_id": message.get("message_id"),
        "disable_web_page_preview": False,
    }
    _telegram_request(token, "sendMessage", payload)


def run_polling() -> None:
    load_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Missing TELEGRAM_BOT_TOKEN in .env")
        sys.exit(1)

    allowed = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS")
    discussion = os.getenv("TELEGRAM_DISCUSSION_CHAT_ID")
    if discussion:
        allowed_chat_ids = {discussion.strip()}
    elif allowed:
        allowed_chat_ids = {item.strip() for item in allowed.split(",") if item.strip()}
    else:
        allowed_chat_ids = None

    offset = 0
    while True:
        payload: dict[str, Any] = {"timeout": 30, "offset": offset}
        try:
            data = _telegram_request(token, "getUpdates", payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8").strip()
            print(body or f"HTTP {exc.code}")
            time.sleep(2)
            continue

        if not data.get("ok"):
            time.sleep(1)
            continue

        updates = data.get("result", [])
        for update in updates:
            offset = max(offset, update.get("update_id", 0) + 1)
            _handle_update(token, update, allowed_chat_ids)


if __name__ == "__main__":
    run_polling()
