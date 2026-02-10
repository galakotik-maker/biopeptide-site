from __future__ import annotations

import argparse
import html
import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterable

from supabase_client import get_supabase_client, load_env


DEFAULT_QUERIES = [
    "Peptides longevity",
    "BPC-157 research",
    "Epitalon benefits",
]

OPEN_WEB_SITES = [
    "forum.longevity.technology",
    "lifespan.io",
    "longevity.technology",
    "selfhacked.com",
    "selfdecode.com",
    "reddit.com/r/Biohackers",
    "reddit.com/r/Peptides",
    "examine.com",
    "med.stanford.edu",
    "hms.harvard.edu",
    "news.mit.edu",
    "nature.com",
    "cell.com",
]

BPPLUS_PROMPT = (
    "Ты — редактор BioPeptidePlus. Переформатируй текст строго в формате:\n"
    "Вводный текст...\n"
    "> Цитата\n"
    "[СУТЬ]\n"
    "...\n"
    "[ПОЛЬЗА]\n"
    "- пункт 1\n"
    "- пункт 2\n"
    "[РЕКОМЕНДАЦИЯ]\n"
    "...\n"
    "Пиши на русском, без JSON."
)


def _openai_format_bpplus(text: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("NEWS_MODEL", "gpt-4o-mini")
    if not api_key:
        return text
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": BPPLUS_PROMPT},
            {"role": "user", "content": text},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return text
    return (choices[0].get("message") or {}).get("content", "").strip() or text

def _fetch_json(url: str, timeout: int = 20) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _post_json(url: str, payload: dict, timeout: int = 20) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _fetch_openapi_columns(url: str, key: str, table: str) -> set[str]:
    endpoint = f"{url.rstrip('/')}/rest/v1/"
    request = urllib.request.Request(endpoint, method="GET")
    request.add_header("Accept", "application/openapi+json")
    request.add_header("apikey", key)
    request.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)

    definition = None
    if isinstance(data, dict):
        if "definitions" in data and isinstance(data["definitions"], dict):
            definition = data["definitions"].get(table)
        if not definition and "components" in data:
            schemas = data.get("components", {}).get("schemas", {})
            if isinstance(schemas, dict):
                definition = schemas.get(table)

    if not isinstance(definition, dict):
        return set()

    properties = definition.get("properties", {})
    if isinstance(properties, dict):
        return set(properties.keys())
    return set()


def _pg_meta_query(url: str, key: str, query: str) -> list[dict]:
    base_paths = ["", "/pg-meta"]
    endpoints = []
    for base in base_paths:
        endpoints.extend(
            [
                (f"{base}/query", {"query": query}),
                (f"{base}/query/", {"query": query}),
                (f"{base}/query", {"sql": query}),
                (f"{base}/query/", {"sql": query}),
                (f"{base}/sql", {"query": query}),
                (f"{base}/sql", {"sql": query}),
            ]
        )
    last_error: tuple[int | None, str] | None = None

    for path, payload in endpoints:
        endpoint = f"{url.rstrip('/')}{path}"
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(endpoint, data=data, method="POST")
        request.add_header("Content-Type", "application/json")
        request.add_header("apikey", key)
        request.add_header("Authorization", f"Bearer {key}")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
            parsed = json.loads(body)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                for key_name in ("result", "data", "rows"):
                    if isinstance(parsed.get(key_name), list):
                        return parsed[key_name]
            return []
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8").strip()
            last_error = (exc.code, body)
            if exc.code not in {404, 401, 403}:
                raise RuntimeError(body or f"pg-meta query failed: HTTP {exc.code}") from exc

    if last_error:
        code, body = last_error
        raise RuntimeError(body or f"pg-meta query failed: HTTP {code}")
    raise RuntimeError("pg-meta query failed: unknown error")


def ensure_translation_columns() -> None:
    load_env()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.")

    columns = _fetch_openapi_columns(url, key, "news_articles")
    if not columns:
        rows = _pg_meta_query(
            url,
            key,
            "select column_name from information_schema.columns "
            "where table_schema='public' and table_name='news_articles';",
        )
        columns = {str(row.get("column_name", "")).strip() for row in rows}

    def _apply_env_pair(en_field: str, ru_field: str) -> bool:
        if en_field in columns and ru_field in columns:
            os.environ["NEWS_ARTICLES_TEXT_EN_FIELD"] = en_field
            os.environ["NEWS_ARTICLES_TEXT_RU_FIELD"] = ru_field
            return True
        return False

    if columns:
        if _apply_env_pair("content_en", "content_ru"):
            return
        if _apply_env_pair("content", "content_ru"):
            return
        if _apply_env_pair("content", "translation_ru"):
            return
        if _apply_env_pair("content", "text_ru"):
            return

        candidates_en = [name for name in columns if name.endswith("_en")]
        for en_field in candidates_en:
            base = en_field[: -len("_en")]
            ru_field = f"{base}_ru"
            if _apply_env_pair(en_field, ru_field):
                return

    missing = []
    if "content_en" not in columns:
        missing.append("content_en")
    if "content_ru" not in columns:
        missing.append("content_ru")

    for column in missing:
        _pg_meta_query(
            url,
            key,
            f"alter table public.news_articles add column if not exists {column} text;",
        )

    os.environ["NEWS_ARTICLES_TEXT_EN_FIELD"] = "content_en"
    os.environ["NEWS_ARTICLES_TEXT_RU_FIELD"] = "content_ru"


def fetch_pubmed_abstracts(id_list: list[str]) -> dict[str, str]:
    if not id_list:
        return {}
    ids = ",".join(id_list)
    efetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&id={ids}&retmode=xml"
    )
    with urllib.request.urlopen(efetch_url, timeout=20) as response:
        xml_payload = response.read().decode("utf-8")

    abstracts: dict[str, str] = {}
    root = ET.fromstring(xml_payload)
    for article in root.findall(".//PubmedArticle"):
        pmid_node = article.find(".//PMID")
        if pmid_node is None or not pmid_node.text:
            continue
        pmid = pmid_node.text.strip()
        abstract_texts = []
        for node in article.findall(".//Abstract/AbstractText"):
            if node.text:
                abstract_texts.append(node.text.strip())
        if abstract_texts:
            abstracts[pmid] = " ".join(abstract_texts)
    return abstracts


def fetch_pubmed_articles(query: str, max_results: int = 10) -> list[dict[str, str]]:
    encoded_query = urllib.parse.quote(query)
    esearch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={encoded_query}&retmode=json&retmax={max_results}"
    )
    esearch_data = _fetch_json(esearch_url)
    id_list = esearch_data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return []

    ids = ",".join(id_list)
    esummary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={ids}&retmode=json"
    )
    esummary_data = _fetch_json(esummary_url)
    abstracts = fetch_pubmed_abstracts(id_list)
    results: list[dict[str, str]] = []

    for pubmed_id in id_list:
        doc = esummary_data.get("result", {}).get(pubmed_id, {})
        title = doc.get("title")
        if not title:
            continue
        summary = abstracts.get(pubmed_id, "")
        results.append(
            {
                "title": title.strip().rstrip("."),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                "summary": summary.strip(),
            }
        )

    return results


def fetch_google_articles(
    query: str, api_key: str, cse_id: str, max_results: int = 10
) -> list[dict[str, str]]:
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": min(max_results, 10),
    }
    url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(
        params
    )
    data = _fetch_json(url)
    items = data.get("items", [])
    results: list[dict[str, str]] = []
    for item in items:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet", "")
        if not title or not link:
            continue
        results.append(
            {"title": title.strip(), "url": link.strip(), "summary": snippet.strip()}
        )
    return results


def fetch_open_web_articles(
    query: str, api_key: str, cse_id: str, max_results: int = 10
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for site in OPEN_WEB_SITES:
        site_query = f"site:{site} {query}"
        results.extend(
            fetch_google_articles(
                site_query, api_key=api_key, cse_id=cse_id, max_results=max_results
            )
        )
        time.sleep(0.2)
    return results


def dedupe_articles(items: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in items:
        url = item.get("url", "").strip()
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        if not url or not title:
            continue
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append({"title": title, "url": url, "summary": summary})
    return unique


def get_translator():
    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    if api_key:
        return ("api", api_key)
    return ("public", None)


def translate_text(text: str, translator: tuple[str, object]) -> str:
    text = text.strip()
    if not text:
        return ""
    mode, resource = translator
    if mode == "api":
        api_key = str(resource)
        url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        payload = {"q": text, "target": "ru", "format": "text"}
        data = _post_json(url, payload)
        translated = (
            data.get("data", {})
            .get("translations", [{}])[0]
            .get("translatedText", "")
        )
        return html.unescape(translated).strip()
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ru",
        "dt": "t",
        "q": text,
    }
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        params
    )
    data = _fetch_json(url)
    segments = data[0] if isinstance(data, list) and data else []
    translated = "".join(segment[0] for segment in segments if segment and segment[0])
    return html.unescape(translated).strip()


def prepare_translated_articles(articles: list[dict[str, str]]) -> list[dict[str, str]]:
    translator = get_translator()
    enriched: list[dict[str, str]] = []
    for item in articles:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        text_en = title if not summary else f"{title}\n\n{summary}"
        text_ru = translate_text(text_en, translator)
        text_ru = _openai_format_bpplus(text_ru)
        enriched.append(
            {
                "title": title,
                "url": item.get("url", "").strip(),
                "text_en": text_en,
                "text_ru": text_ru,
            }
        )
        time.sleep(0.2)
    return enriched


def save_articles_to_supabase(articles: list[dict[str, str]]) -> int:
    if not articles:
        return 0
    supabase = get_supabase_client()
    env_en = os.getenv("NEWS_ARTICLES_TEXT_EN_FIELD")
    env_ru = os.getenv("NEWS_ARTICLES_TEXT_RU_FIELD")
    if env_en and env_ru:
        field_candidates = [(env_en, env_ru)]
    else:
        field_candidates = [
            ("content_en", "content_ru"),
            ("content", "content_ru"),
            ("content", "translation_ru"),
            ("content", "text_ru"),
        ]

    last_error: Exception | None = None
    for text_en_field, text_ru_field in field_candidates:
        payload = []
        for item in articles:
            record = {
                "title": item["title"],
                "url": item["url"],
                text_en_field: item["text_en"],
                text_ru_field: item["text_ru"],
            }
            payload.append(record)

        try:
            response = (
                supabase.table("news_articles")
                .upsert(payload, on_conflict="url")
                .execute()
            )
        except Exception as exc:  # pragma: no cover - API error fallback
            last_error = exc
            continue

        if getattr(response, "error", None):
            last_error = RuntimeError(str(response.error))
            continue

        inserted = response.data or []
        return len(inserted)

    if last_error:
        raise last_error
    return 0


def run_search(
    queries: list[str],
    use_pubmed: bool,
    use_google: bool,
    use_open_web: bool,
    max_results: int,
) -> int:
    load_env()
    ensure_translation_columns()
    articles: list[dict[str, str]] = []

    if use_pubmed:
        for query in queries:
            articles.extend(fetch_pubmed_articles(query, max_results=max_results))
            time.sleep(0.2)

    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if use_google or use_open_web:
        if not api_key or not cse_id:
            raise RuntimeError(
                "Missing GOOGLE_API_KEY or GOOGLE_CSE_ID in .env for Google Search API."
            )

    if use_google:
        for query in queries:
            articles.extend(
                fetch_google_articles(
                    query, api_key=api_key, cse_id=cse_id, max_results=max_results
                )
            )
            time.sleep(0.2)

    if use_open_web:
        for query in queries:
            articles.extend(
                fetch_open_web_articles(
                    query, api_key=api_key, cse_id=cse_id, max_results=max_results
                )
            )

    unique = dedupe_articles(articles)
    translated = prepare_translated_articles(unique)
    return save_articles_to_supabase(translated)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scout-Analyst: fetch, translate, and store articles."
    )
    parser.add_argument(
        "--source",
        choices=["pubmed", "google", "openweb", "global", "all"],
        default="global",
        help="Search source to use.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Max results per query per source.",
    )
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Custom query (can be used multiple times).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    queries = args.query or DEFAULT_QUERIES

    use_pubmed = args.source in {"pubmed", "global", "all"}
    use_google = args.source in {"google", "all"}
    use_open_web = args.source in {"openweb", "global", "all"}
    if args.source == "global":
        use_pubmed = True

    inserted = run_search(
        queries=queries,
        use_pubmed=use_pubmed,
        use_google=use_google,
        use_open_web=use_open_web,
        max_results=args.max_results,
    )
    print(f"Saved {inserted} articles to news_articles.")
    print("Эфир, информация по всему миру собрана и переведена")


if __name__ == "__main__":
    main()
