import ast
import json
import os
import urllib.request
from typing import Optional, List, Dict

from dotenv import load_dotenv


def _request_json(url: str, method: str, headers: dict, payload: Optional[dict] = None) -> List[Dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {error_body}") from exc
    parsed = json.loads(body)
    return parsed if isinstance(parsed, list) else []


def _fetch_columns(base_url: str, headers: dict) -> List[str]:
    endpoint = f"{base_url}/rest/v1/"
    req = urllib.request.Request(endpoint, method="GET", headers={**headers, "Accept": "application/openapi+json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    definitions = data.get("definitions") or data.get("components", {}).get("schemas", {})
    table = definitions.get("journal_posts") if isinstance(definitions, dict) else None
    props = table.get("properties") if isinstance(table, dict) else None
    if isinstance(props, dict):
        return list(props.keys())
    return []


def _to_tagged(text: str) -> str:
    if not text:
        return ""
    raw = text.strip()
    if not raw.startswith("{") or "introduction" not in raw:
        return raw
    try:
        data = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw
    if not isinstance(data, dict):
        return raw
    intro = str(data.get("introduction", "")).strip()
    essence = str(data.get("essence", "")).strip()
    conclusion = str(data.get("conclusion", "")).strip()
    parts = []
    if intro:
        parts.append(intro)
    if essence:
        parts.append("[СУТЬ]\n" + essence)
    if conclusion:
        parts.append("[РЕКОМЕНДАЦИЯ]\n" + conclusion)
    return "\n\n".join(parts).strip() or raw


def main() -> None:
    load_dotenv()
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.")

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    columns = _fetch_columns(url, headers)
    text_field = "description"
    for candidate in ("description", "summary", "content"):
        if candidate in columns:
            text_field = candidate
            break

    fetch_url = (
        f"{url}/rest/v1/journal_posts"
        f"?select=id,{text_field}&order=created_at.desc&limit=2"
    )
    rows = _request_json(fetch_url, "GET", headers)
    if not rows:
        print("Нет записей для миграции.")
        return

    for row in rows:
        post_id = row.get("id")
        description = str(row.get(text_field) or "")
        new_text = _to_tagged(description)
        if not post_id or not new_text:
            continue
        patch_url = f"{url}/rest/v1/journal_posts?id=eq.{post_id}"
        payload = {text_field: new_text}
        _request_json(patch_url, "PATCH", headers, payload)
        print(f"Updated post {post_id}")


if __name__ == "__main__":
    main()
