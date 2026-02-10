import argparse
import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional


class RateLimitError(Exception):
    def __init__(self, retry_after: Optional[float] = None) -> None:
        super().__init__("Rate limit exceeded")
        self.retry_after = retry_after

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


DEFAULT_SYSTEM_PROMPT = (
    "Ты — научный референт BioPeptidePlus. "
    "Пиши по-русски, сухо и точно. "
    "Структура: Механизм, Эффекты, Применение. "
    "Не выдумывай данные; если информации нет, так и напиши: "
    "'Данные в источнике отсутствуют'."
)


def _pretty_name(file_stem: str) -> str:
    return file_stem.replace("_", " ").replace("-", " ").strip()


def _openai_generate(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return ""
    return (choices[0].get("message") or {}).get("content", "").strip()


def _gemini_generate(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "contents": [{"role": "user", "parts": [{"text": DEFAULT_SYSTEM_PROMPT + "\n\n" + prompt}]}],
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
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace").strip()
        if error_body:
            print(error_body)
        if exc.code == 429 and error_body:
            try:
                parsed = json.loads(error_body)
                retry_info = parsed.get("error", {}).get("details", [])
                retry_after = None
                for item in retry_info:
                    if item.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                        delay = item.get("retryDelay")
                        if isinstance(delay, str) and delay.endswith("s"):
                            retry_after = float(delay[:-1])
                raise RateLimitError(retry_after=retry_after)
            except (json.JSONDecodeError, ValueError):
                raise RateLimitError() from exc
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


def _generate_text(prompt: str, provider: str, model: str) -> str:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")
        return _openai_generate(prompt, api_key, model)
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY or GOOGLE_API_KEY")
        if not api_key.startswith("AIza"):
            print("Возможно, это не ключ Gemini")
        return _gemini_generate(prompt, api_key, model)
    raise RuntimeError(f"Unknown provider: {provider}")

def _list_gemini_models(
    api_key: str,
) -> tuple[list[tuple[str, list[str]]], list[str]]:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models"
        f"?key={api_key}"
    )
    request = urllib.request.Request(endpoint, method="GET")
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    models = parsed.get("models", [])
    all_models: list[tuple[str, list[str]]] = []
    generate_models: list[str] = []
    for item in models:
        name = item.get("name")
        if not isinstance(name, str):
            continue
        clean_name = name.replace("models/", "")
        methods = item.get("supportedGenerationMethods") or []
        if not isinstance(methods, list):
            methods = []
        methods = [m for m in methods if isinstance(m, str)]
        all_models.append((clean_name, methods))
        if "generateContent" in methods:
            generate_models.append(clean_name)
    return all_models, generate_models


def _pick_gemini_model(preferred: str, available: list[str]) -> Optional[str]:
    candidates = [
        preferred,
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-1.5-pro",
        "gemini-pro",
    ]
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def _generate_with_retries(
    prompt: str, provider: str, model: str, max_retries: int = 5
) -> str:
    backoff_seconds = 5
    for attempt in range(1, max_retries + 1):
        try:
            return _generate_text(prompt, provider, model)
        except RateLimitError as exc:
            if attempt >= max_retries:
                raise
            wait_for = exc.retry_after or backoff_seconds
            print(
                f"Лимит достигнут, жду {int(wait_for)} секунд перед повтором..."
            )
            time.sleep(wait_for)
            backoff_seconds *= 2
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            if attempt >= max_retries:
                raise
            print(
                f"Лимит достигнут, жду {backoff_seconds} секунд перед повтором..."
            )
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
        except urllib.error.URLError:
            if attempt >= max_retries:
                raise
            print(
                f"Сеть недоступна, жду {backoff_seconds} секунд перед повтором..."
            )
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
    return ""


def _build_prompt(peptide_name: str) -> str:
    return (
        "Сформируй экспертное описание пептида.\n"
        f"Пептид: {peptide_name}\n"
        "Выдай текст без лишней воды, короткими абзацами.\n"
        "Структура строго:\n"
        "Механизм: ...\n"
        "Эффекты: ...\n"
        "Применение: ...\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mass refill peptide knowledge base using LLM."
    )
    parser.add_argument(
        "--db-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_db"),
        help="Path to research_db folder",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini"],
        default="openai",
        help="LLM provider to use",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="Model name (OpenAI or Gemini)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds",
    )
    args = parser.parse_args()

    if args.provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise SystemExit("Missing GEMINI_API_KEY or GOOGLE_API_KEY")
        if not api_key.startswith("AIza"):
            print("Возможно, это не ключ Gemini")
        try:
            all_models, generate_models = _list_gemini_models(api_key)
            if all_models:
                print("Доступные модели Gemini:")
                for name, methods in all_models:
                    suffix = f" ({', '.join(methods)})" if methods else ""
                    print(f"- {name}{suffix}")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace").strip()
            if error_body:
                print(error_body)
            raise SystemExit("Не удалось получить список моделей Gemini") from exc

        preferred = args.model
        if preferred == "gpt-4o":
            preferred = "gemini-1.5-flash"
        picked = _pick_gemini_model(preferred, generate_models)
        if not picked:
            raise SystemExit("Нет доступных моделей Gemini для generateContent")
        if picked != args.model:
            print(f"Gemini: использую модель {picked}.")
        args.model = picked

    if not os.path.isdir(args.db_dir):
        raise SystemExit(f"research_db not found: {args.db_dir}")

    files = sorted(
        f
        for f in os.listdir(args.db_dir)
        if f.lower().endswith(".txt")
        and os.path.isfile(os.path.join(args.db_dir, f))
    )
    if not files:
        print("No .txt files found in research_db.")
        return

    for filename in files:
        file_path = os.path.join(args.db_dir, filename)
        stem = os.path.splitext(filename)[0]
        peptide_name = _pretty_name(stem)
        try:
            with open(file_path, "r", encoding="utf-8") as existing:
                existing_text = existing.read()
            if (
                len(existing_text) > 500
                and "Данные в источнике отсутствуют" not in existing_text
            ):
                print(f"Пропускаю {filename}, файл уже заполнен.")
                continue
        except Exception:
            pass
        prompt = _build_prompt(peptide_name)
        try:
            text = _generate_with_retries(prompt, args.provider, args.model)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            print(f"[ERROR] {filename}: {exc}")
            continue

        if not text.strip():
            print(f"[WARN] {filename}: empty response, skipping")
            continue

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        print(f"[OK] {filename} updated")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
