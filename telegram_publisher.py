from __future__ import annotations

import argparse
import json
import os
import sys
import datetime
import urllib.error
import urllib.parse
import urllib.request
import re

from supabase_client import get_supabase_client, load_env


SOURCE_MAP = {
    "pubmed.ncbi.nlm.nih.gov": "PubMed",
    "sciencedirect.com": "ScienceDirect",
    "nature.com": "Nature",
    "cell.com": "Cell",
    "thelancet.com": "The Lancet",
    "news.harvard.edu": "Harvard Medical School",
    "hms.harvard.edu": "Harvard Medical School",
    "med.stanford.edu": "Stanford Medicine",
    "news.stanford.edu": "Stanford Medicine",
    "news.mit.edu": "MIT News",
    "hopkinsmedicine.org": "Johns Hopkins",
    "hub.jhu.edu": "Johns Hopkins",
}

DISCOVERY_TOPICS = [
    "longevity peptides",
    "mitochondrial repair",
    "neuroprotection",
    "senolytics",
    "metabolic health",
    "glucose",
    "lipid profile",
    "sleep optimization",
    "thermal exposure",
    "sauna",
    "cold exposure",
    "preventive diagnostics",
]

ASSORTMENT_PEPTIDES = [
    "Epitalon",
    "BPC-157",
    "SS-31",
    "Elamipretide",
]
UNIVERSITY_MAP = {
    "news.harvard.edu": "Harvard Medical School",
    "hms.harvard.edu": "Harvard Medical School",
    "med.stanford.edu": "Stanford Medicine",
    "news.stanford.edu": "Stanford Medicine",
    "news.mit.edu": "MIT News",
    "hopkinsmedicine.org": "Johns Hopkins",
    "hub.jhu.edu": "Johns Hopkins",
}

TOP_PRIORITY_DOMAINS = {
    "nature.com",
    "cell.com",
    "hms.harvard.edu",
    "news.harvard.edu",
    "med.stanford.edu",
    "news.stanford.edu",
    "news.mit.edu",
}

def send_message(
    token: str, chat_id: str, text: str, article_url: str | None = None
) -> None:
    telegram_api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if article_url:
        payload["reply_markup"] = json.dumps(
            {"inline_keyboard": [[{"text": "Оригинал статьи", "url": article_url}]]},
            ensure_ascii=True,
        )
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(telegram_api_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8").strip()
        if body:
            print(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8").strip()
        print(body or f"HTTP {exc.code}")
        raise SystemExit(1) from exc


def send_photo(
    token: str,
    chat_id: str,
    photo_url: str,
    caption: str,
    article_url: str | None = None,
) -> None:
    telegram_api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    if article_url:
        payload["reply_markup"] = json.dumps(
            {"inline_keyboard": [[{"text": "Оригинал статьи", "url": article_url}]]},
            ensure_ascii=True,
        )
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(telegram_api_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8").strip()
        if body:
            print(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8").strip()
        print(body or f"HTTP {exc.code}")
        raise SystemExit(1) from exc


def generate_image_prompt(article: dict) -> str:
    title = str(article.get("title", "")).strip()
    summary = str(article.get("summary", "")).strip()
    content = str(article.get("content", "")).strip()
    base = title or summary or "biomedical research"
    if content:
        base = f"{base}. {content[:400]}"
    prompt = (
        "High-tech biology illustration inspired by: "
        f"{base}. "
        "Style: scientific premium, clean lines, minimalistic, futuristic, laboratory-grade. "
        "Color palette: white, steel, deep blue, cold tones. "
        "Elements: cellular structures, mitochondrial membranes repair, peptide chains, lab vials, microscopy textures. "
        "No people, no faces, no text."
    )
    return prompt


def generate_image_prompt_from_text(text_ru: str, premium: bool = False) -> str:
    base = _normalize_text(text_ru)
    if len(base) > 600:
        base = base[:600]
    detail = (
        "ultra-detailed, premium materials, precise molecular rendering"
        if premium
        else "minimalistic, clean, restrained detail"
    )
    prompt = (
        "High-tech biology illustration inspired by: "
        f"{base}. "
        f"Style: scientific premium, clean lines, futuristic, laboratory-grade, {detail}. "
        "Color palette: white, steel, deep blue, cold tones. "
        "Elements: cellular structures, mitochondrial membranes repair, peptide chains, lab vials, microscopy textures. "
        "No people, no faces, no text."
    )
    return prompt


def generate_image_url(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Missing OPENAI_API_KEY. Provide it to enable image generation.")
        return None

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=data, method="POST"
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    data_items = parsed.get("data", [])
    if not data_items:
        return None
    return data_items[0].get("url")

def _fetch_openapi_tables(url: str, key: str) -> set[str]:
    endpoint = f"{url.rstrip('/')}/rest/v1/"
    request = urllib.request.Request(endpoint, method="GET")
    request.add_header("Accept", "application/openapi+json")
    request.add_header("apikey", key)
    request.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    if isinstance(data, dict):
        if "definitions" in data and isinstance(data["definitions"], dict):
            return set(data["definitions"].keys())
        if "components" in data and isinstance(data["components"], dict):
            schemas = data["components"].get("schemas", {})
            if isinstance(schemas, dict):
                return set(schemas.keys())
    return set()


def _pg_meta_query(url: str, key: str, query: str) -> None:
    base_paths = ["", "/pg-meta"]
    endpoints = []
    for base in base_paths:
        endpoints.extend(
            [
                (f"{base}/query", {"query": query}),
                (f"{base}/query/", {"query": query}),
                (f"{base}/query", {"sql": query}),
                (f"{base}/query/", {"sql": query}),
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
                response.read()
            return
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8").strip()
            last_error = (exc.code, body)
            if exc.code not in {404, 401, 403}:
                raise RuntimeError(body or f"pg-meta query failed: HTTP {exc.code}") from exc

    if last_error:
        code, body = last_error
        raise RuntimeError(body or f"pg-meta query failed: HTTP {code}")
    raise RuntimeError("pg-meta query failed: unknown error")


def ensure_queue_tables() -> None:
    load_env()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.")

    tables = _fetch_openapi_tables(url, key)
    required = {"publish_queue", "publish_log"}
    missing = required - tables
    if not missing:
        return

    create_sql = {
        "publish_queue": """
        create table if not exists public.publish_queue (
          id uuid primary key default gen_random_uuid(),
          article_url text not null,
          title text,
          source text,
          priority int default 0,
          full_message text not null,
          hook text,
          site_announcement text,
          status text default 'queued',
          created_at timestamptz not null default now()
        );
        """.strip(),
        "publish_log": """
        create table if not exists public.publish_log (
          id uuid primary key default gen_random_uuid(),
          article_url text not null,
          chat_id text not null,
          published_at timestamptz not null default now()
        );
        """.strip(),
    }

    try:
        for table in missing:
            _pg_meta_query(url, key, create_sql[table])
    except Exception:
        print("Missing queue tables. Create them manually:")
        for table in missing:
            print(create_sql[table])
        raise SystemExit(1)
def fetch_latest_articles(
    limit: int = 6, query: str | None = None, topics: list[str] | None = None
) -> list[dict]:
    supabase = get_supabase_client()
    request = (
        supabase.table("news_articles")
        .select("*")
        .order("created_at", desc=True)
    )
    if topics:
        filters = []
        for topic in topics:
            term = topic.replace(",", " ").strip()
            if not term:
                continue
            filters.append(f"title.ilike.%{term}%")
            filters.append(f"content.ilike.%{term}%")
        if filters:
            request = request.or_(",".join(filters))
    elif query:
        request = request.or_(f"title.ilike.%{query}%,content.ilike.%{query}%")
    response = request.limit(100).execute()
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    items = response.data or []
    filtered = []
    for item in items:
        url = str(item.get("url", "")).lower()
        if any(domain in url for domain in SOURCE_MAP.keys()):
            filtered.append(item)
    return filtered[:limit]


def _translate_text(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    if api_key:
        endpoint = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        payload = {"q": text, "target": "ru", "format": "text"}
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(endpoint, data=data, method="POST")
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
        parsed = json.loads(body)
        translated = (
            parsed.get("data", {})
            .get("translations", [{}])[0]
            .get("translatedText", "")
        )
        return translated.strip()

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
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    segments = parsed[0] if isinstance(parsed, list) and parsed else []
    translated = "".join(segment[0] for segment in segments if segment and segment[0])
    return translated.strip()


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _detect_source(article_url: str) -> str:
    lower = article_url.lower()
    for domain, name in SOURCE_MAP.items():
        if domain in lower:
            return name
    return "Источник"


def _detect_university(article_url: str) -> str | None:
    lower = article_url.lower()
    for domain, name in UNIVERSITY_MAP.items():
        if domain in lower:
            return name
    return None


def _is_top_priority_source(article_url: str) -> bool:
    lower = article_url.lower()
    return any(domain in lower for domain in TOP_PRIORITY_DOMAINS)


def _first_sentence(text: str) -> str:
    text = " ".join(text.strip().split())
    if not text:
        return ""
    for splitter in (". ", "? ", "! "):
        if splitter in text:
            return text.split(splitter, 1)[0].strip() + splitter.strip()
    return text


def _truncate(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def _contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in keywords)


def _missing_data_lines(base_text: str) -> list[str]:
    keywords_dose = ["mg", "mcg", "мг", "мкг", "dose", "dosage", "доз", "концентрац"]
    keywords_effects = [
        "adverse",
        "side effect",
        "toxicity",
        "safety",
        "побочн",
        "нежелатель",
        "токсич",
        "безопасн",
    ]
    keywords_mechanism = [
        "mechanism",
        "pathway",
        "signal",
        "emt",
        "ros",
        "афк",
        "механизм",
        "сигнальн",
        "путь",
    ]

    missing = []
    if not _contains_any(base_text, keywords_dose):
        missing.append("Дозировки: Данные в источнике отсутствуют")
    if not _contains_any(base_text, keywords_effects):
        missing.append("Побочные эффекты: Данные в источнике отсутствуют")
    if not _contains_any(base_text, keywords_mechanism):
        missing.append("Механизм действия: Данные в источнике отсутствуют")
    return missing


def _lifestyle_synergy_line(base_text: str) -> str:
    keywords = [
        "diet",
        "nutrition",
        "sleep",
        "exercise",
        "physical activity",
        "training",
        "sauna",
        "cold exposure",
        "therm",
        "glucose",
        "lipid",
        "метабол",
        "глюкоз",
        "липид",
        "сон",
        "питани",
        "физическ",
        "сауна",
        "холод",
        "термо",
    ]
    if _contains_any(base_text, keywords):
        return "Синергия с образом жизни: Указано в источнике."
    return "Синергия с образом жизни: Данные отсутствуют"


def _annotate_mechanisms(text: str, article_url: str) -> tuple[str, str]:
    keywords = [
        "ЕМТ",
        "EMT",
        "ROS",
        "АФК",
        "reactive oxygen species",
    ]
    found = False
    updated = text
    for keyword in keywords:
        if keyword in updated:
            updated = updated.replace(keyword, f"{keyword} (1)", 1)
            found = True
    refs = ""
    if found:
        refs = f'Источники: <a href="{_escape_html(article_url)}">1</a>'
    return updated, refs


def _extract_lead_researcher(text: str) -> str | None:
    normalized = _normalize_text(text)
    if not normalized:
        return None
    patterns = [
        r"Professor\s+([A-Z][a-z]+)",
        r"Prof\.\s*([A-Z][a-z]+)",
        r"Dr\.\s*([A-Z][a-z]+)",
        r"by\s+([A-Z][a-z]+)\s+[A-Z][a-z]+",
        r"led by\s+([A-Z][a-z]+)\s+[A-Z][a-z]+",
    ]
    import re

    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group(1)
    return None


def _extract_peptide_names(text: str) -> set[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return set()
    candidates = set(re.findall(r"\b[A-Z]{2,}-\d+\b", normalized))
    for name in ASSORTMENT_PEPTIDES:
        if name in normalized:
            candidates.add(name)
    return {item.strip() for item in candidates if item.strip()}


def _known_peptides(supabase) -> set[str]:
    response = supabase.table("news_articles").select("title").limit(1000).execute()
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    known: set[str] = set()
    for row in response.data or []:
        title = str(row.get("title", "")).strip()
        known |= _extract_peptide_names(title)
    return known


def _is_new_peptide(article: dict, known: set[str]) -> bool:
    title = str(article.get("title", "")).strip()
    summary = str(article.get("summary", "")).strip()
    names = _extract_peptide_names(f"{title} {summary}")
    if not names:
        return False
    return names.isdisjoint(known)


def _innovation_score(article: dict) -> int:
    text = _normalize_text(
        " ".join(
            str(article.get(key, "")).strip()
            for key in ("title", "summary", "content", "content_en")
        )
    ).lower()
    score = 0
    if "high bioavailability" in text or "bioavailability" in text:
        score += 2
    if any(term in text for term in ("mammal", "mammalian", "mouse", "mice", "rat", "rodent")):
        score += 2
    return score


def _is_peptide_post(article: dict) -> bool:
    text = " ".join(
        str(article.get(key, "")).strip()
        for key in ("title", "summary", "content", "content_en", "full_message")
    )
    return bool(_extract_peptide_names(text))


def _biohacking_score(article: dict) -> float:
    text = _normalize_text(
        " ".join(
            str(article.get(key, "")).strip()
            for key in ("title", "summary", "content", "content_en")
        )
    ).lower()
    biohack_terms = [
        "sleep",
        "sauna",
        "cold exposure",
        "therm",
        "nutrition",
        "diet",
        "exercise",
        "training",
        "glucose",
        "lipid",
        "metabolic",
        "сон",
        "сауна",
        "питани",
        "физическ",
        "глюкоз",
        "липид",
        "метабол",
        "холод",
        "термо",
    ]
    return 1.0 if any(term in text for term in biohack_terms) else 0.0


def _peptide_relevance_score(article: dict) -> float:
    return 1.0 if _is_peptide_post(article) else 0.0


def _priority_score(article: dict) -> float:
    return 0.7 * _peptide_relevance_score(article) + 0.3 * _biohacking_score(article)


def _is_clinical_study(article: dict) -> bool:
    text = _normalize_text(
        " ".join(
            str(article.get(key, "")).strip()
            for key in ("title", "summary", "content", "content_en")
        )
    ).lower()
    return any(
        term in text
        for term in (
            "clinical",
            "randomized",
            "trial",
            "phase",
            "patients",
            "клиническ",
            "рандом",
            "испыта",
            "фаза",
            "пациент",
        )
    )


def _critical_peptide_update(article: dict) -> bool:
    text = " ".join(
        str(article.get(key, "")).strip()
        for key in ("title", "summary", "content", "content_en")
    )
    names = _extract_peptide_names(text)
    return bool(names.intersection(set(ASSORTMENT_PEPTIDES))) and _is_clinical_study(
        article
    )


def _extract_conclusion_en(base_en: str) -> str:
    keywords = [
        "conclusion",
        "results",
        "summary",
        "we found that",
        "treatment improved",
    ]
    normalized = _normalize_text(base_en)
    if not normalized:
        return ""
    sentences = []
    current = []
    for char in normalized:
        current.append(char)
        if char in ".!?":
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []
    if current:
        sentence = "".join(current).strip()
        if sentence:
            sentences.append(sentence)

    matches = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in keywords):
            matches.append(sentence)
    return " ".join(matches).strip()


def _publication_year(article: dict) -> int | None:
    for key in ("published_at", "publication_date", "created_at"):
        value = str(article.get(key, "")).strip()
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _year_in_range(article: dict, start: int, end: int) -> bool:
    year = _publication_year(article)
    if year is None:
        return False
    return start <= year <= end


def _is_meta_or_systematic(title: str, summary: str) -> bool:
    haystack = f"{title} {summary}".lower()
    return "meta-analysis" in haystack or "systematic review" in haystack


def _impact_factor(article: dict) -> float | None:
    for key in ("impact_factor", "journal_if", "if"):
        value = article.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _priority_sort(article: dict) -> tuple[int, int, int]:
    title = str(article.get("title", "")).strip()
    summary = str(article.get("summary", "")).strip()
    year = _publication_year(article) or 0
    is_meta = 1 if _is_meta_or_systematic(title, summary) else 0
    is_recent = 1 if 2024 <= year <= 2026 else 0
    has_high_if = 1 if (_impact_factor(article) or 0.0) > 10 else 0
    return (is_meta, is_recent, year * 100 + has_high_if)


def format_article_message(
    article: dict, topic: str | None = None
) -> tuple[str, str | None, str, str]:
    title = str(article.get("title", "")).strip()
    url = str(article.get("url", "")).strip()
    content_en = str(article.get("content_en", "") or article.get("content", "")).strip()
    content_ru = str(article.get("content_ru", "")).strip()
    summary_en = str(article.get("summary", "")).strip()

    source = _detect_source(url)
    base_en = content_en or summary_en or title

    if content_ru:
        summary_ru = content_ru
    else:
        summary_ru = _translate_text(base_en)

    summary_ru, refs = _annotate_mechanisms(summary_ru, url)
    lead_researcher = _extract_lead_researcher(content_en or summary_en or "")
    if lead_researcher:
        summary_ru = f"Группа профессора {lead_researcher} обнаружила: {summary_ru}"
    else:
        summary_ru = f"Ведущий исследователь: Данные в источнике отсутствуют. {summary_ru}"
    base_ru = _normalize_text(summary_ru)
    conclusion_en = _extract_conclusion_en(base_en)
    conclusion_ru = _translate_text(conclusion_en) if conclusion_en else "Данные отсутствуют"
    missing_lines = _missing_data_lines(base_ru)
    lifestyle_line = _lifestyle_synergy_line(base_ru)
    if missing_lines:
        conclusion_ru = "\n".join([conclusion_ru] + missing_lines)
    conclusion_ru = "\n".join([conclusion_ru, lifestyle_line])

    high_if = (_impact_factor(article) or 0.0) > 10
    badge = "💎 Исследование высшего уровня доказательности\n" if high_if else ""
    critical_badge = (
        "🔥 КРИТИЧЕСКИ ВАЖНОЕ ОБНОВЛЕНИЕ\n"
        if article.get("is_critical_update")
        else ""
    )

    university = _detect_university(url)
    if university:
        header = f"🏛 УНИВЕРСИТЕТСКИЙ ПРОРЫВ: {university}"
    else:
        header = title

    hook_source = _normalize_text(summary_ru)
    hook = _first_sentence(hook_source) if hook_source else "Данные отсутствуют"
    if article.get("is_new_discovery"):
        hook = f"Новое имя в биохакинге: разбираем исследование {title}"
    hook_block = (
        f"<blockquote>{_escape_html(hook)}\n"
        f'<a href="https://BioPeptidePlus.com">Аналитика от проекта BioPeptidePlus</a>'
        f"</blockquote>\n"
    )

    cta = "Подробный разбор и профессиональная версия исследования — на BioPeptidePlus.com"

    discovery_tag = "NEW DISCOVERY\n" if article.get("is_new_discovery") else ""

    peptide_names = _extract_peptide_names(
        " ".join(
            str(article.get(key, "")).strip()
            for key in ("title", "summary", "content", "content_en")
        )
    )
    peptide_line = ""
    if _biohacking_score(article) > 0:
        if peptide_names:
            peptide_line = f"Релевантный пептид: {', '.join(sorted(peptide_names))}\n"
        else:
            peptide_line = "Релевантный пептид: Данные отсутствуют\n"

    message = (
        f"{hook_block}{_escape_html(header)}\n"
        f'Источник: <a href="{_escape_html(url)}">{_escape_html(source)}</a>\n'
        f"Тема: {_escape_html(topic or '')}\n"
        f"{discovery_tag}"
        f"{critical_badge}"
        f"{badge}"
        f"Научное резюме: {_escape_html(summary_ru)}\n\n"
        f"{_escape_html(peptide_line)}"
        f"Практический вывод: {_escape_html(conclusion_ru)}\n\n"
        f"{_escape_html(cta)}"
    )
    if refs:
        message = f"{message}\n\n{refs}"
    site_announcement = f"{hook}\n{url}".strip()
    return message, url or None, hook, site_announcement


def _today_iso() -> str:
    return datetime.datetime.utcnow().date().isoformat()


def _get_today_published_count(supabase, chat_id: str) -> int:
    today = _today_iso()
    response = (
        supabase.table("publish_log")
        .select("id", count="exact")
        .eq("chat_id", chat_id)
        .gte("published_at", today)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    return int(getattr(response, "count", 0) or 0)


def _queue_exists(supabase, article_url: str) -> bool:
    response = (
        supabase.table("publish_queue")
        .select("id")
        .eq("article_url", article_url)
        .limit(1)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    return bool(response.data)


def _queue_article(supabase, record: dict) -> None:
    response = supabase.table("publish_queue").insert(record).execute()
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))


def _fetch_queue(supabase, limit: int) -> list[dict]:
    response = (
        supabase.table("publish_queue")
        .select("*")
        .eq("status", "queued")
        .order("priority", desc=True)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    return response.data or []


def _mark_published(supabase, queue_id: str, article_url: str, chat_id: str) -> None:
    response = (
        supabase.table("publish_queue")
        .update({"status": "published"})
        .eq("id", queue_id)
        .execute()
    )
    if getattr(response, "error", None):
        raise RuntimeError(str(response.error))
    _log_published(supabase, article_url, chat_id)


def _log_published(supabase, article_url: str, chat_id: str) -> None:
    log = supabase.table("publish_log").insert(
        {"article_url": article_url, "chat_id": chat_id}
    ).execute()
    if getattr(log, "error", None):
        raise RuntimeError(str(log.error))


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish peptide research posts.")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--year-start", type=int, default=0)
    parser.add_argument("--year-end", type=int, default=0)
    parser.add_argument("--max-publish", type=int, default=2)
    args = parser.parse_args()

    load_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID in .env")
        sys.exit(1)

    ensure_queue_tables()
    topic = args.topic.strip()
    query = args.query.strip()
    supabase = get_supabase_client()
    topics = None
    if not query:
        topics = DISCOVERY_TOPICS
    articles = fetch_latest_articles(limit=100, query=query or None, topics=topics)
    if not articles:
        print("No articles found to publish.")
        return

    if args.year_start and args.year_end:
        articles = [
            article
            for article in articles
            if _year_in_range(article, args.year_start, args.year_end)
        ]
        if not articles:
            print("No articles found in requested year range.")
            return

    known = _known_peptides(supabase)
    for article in articles:
        article["is_new_discovery"] = _is_new_peptide(article, known)
        article["is_critical_update"] = _critical_peptide_update(article)

    articles.sort(
        key=lambda item: (
            1 if item.get("is_critical_update") else 0,
            1 if _is_top_priority_source(str(item.get("url", ""))) else 0,
            _priority_score(item),
            _innovation_score(item),
            _priority_sort(item),
        ),
        reverse=True,
    )
    if len(articles) >= 10:
        args.max_publish = min(args.max_publish, 2)

    for article in articles:
        message, url, hook, site_announcement = format_article_message(
            article, topic=topic or None
        )
        if not message or not url:
            continue
        if _queue_exists(supabase, url):
            continue
        if article.get("is_critical_update"):
            prompt = generate_image_prompt_from_text(message, premium=_is_peptide_post(article))
            image_url = generate_image_url(prompt)
            if not image_url:
                print("Image generation unavailable; skipping publish.")
                return
            send_photo(token, chat_id, image_url, "", article_url=None)
            send_message(token, chat_id, message, article_url=url)
            _log_published(supabase, url, chat_id)
            continue
        priority = 3 if _is_top_priority_source(url) else 2 if _detect_university(url) or (_impact_factor(article) or 0) > 10 else 1
        record = {
            "article_url": url,
            "title": article.get("title"),
            "source": _detect_source(url),
            "priority": priority,
            "full_message": message,
            "hook": hook,
            "site_announcement": site_announcement,
            "status": "queued",
        }
        _queue_article(supabase, record)

    published_today = _get_today_published_count(supabase, chat_id)
    remaining = max(0, min(args.max_publish, 2) - published_today)
    if remaining == 0:
        print("Daily limit reached; items queued.")
        return

    queue_items = _fetch_queue(supabase, remaining)
    for item in queue_items:
        full_message = item.get("full_message", "")
        prompt = generate_image_prompt_from_text(
            full_message, premium=_is_peptide_post(item)
        )
        image_url = generate_image_url(prompt)
        if not image_url:
            print("Image generation unavailable; skipping publish.")
            return
        send_photo(token, chat_id, image_url, "", article_url=None)
        send_message(
            token,
            chat_id,
            full_message,
            article_url=item.get("article_url"),
        )
        _mark_published(supabase, item["id"], item.get("article_url", ""), chat_id)
        if item.get("site_announcement"):
            print(f"Site announcement:\n{item['site_announcement']}")


if __name__ == "__main__":
    main()
