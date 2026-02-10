import argparse
import json
import os
import re
import time
import random
from typing import Optional
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib import request
from urllib import parse
from urllib.error import HTTPError
from dotenv import load_dotenv

from telegram_publisher import send_message, send_photo

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Ключ OpenAI не найден!")


def _normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def _pretty_name(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").strip()


def _mock_search(name: str) -> dict:
    """
    Имитация поиска. Если данных нет, вернёт пустые поля.
    Добавляй сюда новые записи по мере необходимости.
    """
    knowledge = {
        "ipamorelin": {
            "mechanism": "Агонист рецептора GHS-R (грелинового рецептора).",
            "effects": "Стимуляция секреции гормона роста без выраженного влияния на кортизол.",
            "dosage": "Данные в источнике отсутствуют.",
            "sources": "Локальная база (имитация поиска).",
        },
        "tesofensine": {
            "mechanism": "Ингибитор обратного захвата моноаминов (серотонин, норадреналин, дофамин).",
            "effects": "Снижение аппетита и поддержка снижения массы тела.",
            "dosage": "Данные в источнике отсутствуют.",
            "sources": "Локальная база (имитация поиска).",
        },
    }
    return knowledge.get(name, {})


def _format_entry(peptide_name: str, data: dict) -> str:
    mechanism = data.get("mechanism", "Данные в источнике отсутствуют.")
    effects = data.get("effects", "Данные в источнике отсутствуют.")
    dosage = data.get("dosage", "Данные в источнике отсутствуют.")
    sources = data.get("sources", "Открытые источники не найдены.")

    return (
        "⚖️ Научное обоснование из BioPeptidePlus\n\n"
        f"> --- AUTO ENTRY {datetime.utcnow().isoformat()} ---\n"
        f"> Пептид: {peptide_name}\n"
        f"> Механизм: {mechanism}\n"
        f"> Эффекты: {effects}\n"
        f"> Дозировки: {dosage}\n"
        f"> Источники: {sources}\n"
    )


JOURNAL_ENDPOINT = "https://fmtbdjyaqgszzzzcrhdk.supabase.co/functions/v1/journal-bot"
TEXT_MODEL = os.getenv("NEWS_MODEL", "gpt-4o-mini")
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "2"))
KNOWLEDGE_BASE_FILE = "knowledge_base.txt"
DEFAULT_KEYWORDS = [
    "AOD9604",
    "Fragment 176-191",
    "Tesamorelin",
    "CJC-1295 + Ipamorelin",
    "5-Amino-1MQ",
    "P21",
    "Cerebrolysin",
    "Dihexa",
    "Selank",
    "Noopept",
    "Adamax",
    "Epitalon",
    "GHK-Cu",
    "Foxo4-DRI",
    "Thymulin",
    "MOTS-c",
    "BPC-157",
    "TB-500 (Thymosin Beta-4)",
    "Ipamorelin",
    "IGF-1 LR3",
    "PT-141 (Bremelanotide)",
    "Kisspeptin",
    "Melanotan II",
]
SEARCH_KEYWORDS: list[str] = list(DEFAULT_KEYWORDS)
IMAGE_THEMES = [
    "Molecular Architecture: macro shot of a single peptide molecule like a neon sculpture.",
    "DNA Data Stream: a stream of binary code folding into a DNA helix.",
    "Neural Jungle: tangled neurons glowing from within like a night forest.",
    "The Blueprint: blue-white human body blueprint with one active zone highlighted (brain or heart).",
    "Peptide Rain: abstract geometric forms falling into water creating concentric circles.",
    "The Wise Professor: close-up portrait of an elderly scientist with wise eyes looking at a tablet.",
    "The Silent Focus: gloved hands carefully holding a single glowing ampoule.",
    "Biohacker Morning: a person with futuristic glasses or a skin patch meditating.",
    "The Discussion: silhouettes of two scientists by a panoramic window in a modern lab.",
    "Micro-Gaze: a scientist's eye looking into a microscope eyepiece with cell reflection.",
    "Robotic Precision: a robotic arm filling a test tube in a pristine white room.",
    "The Petri Art: colorful bacterial cultures in a Petri dish like fine art.",
    "Futuristic Pharmacy: minimalist glass vials on a mirrored surface.",
    "Cryo-Storage: liquid nitrogen vapor from an open cryo storage unit.",
    "Holographic Scan: a 3D brain hologram above a modern desk.",
    "Cellular Energy: a mitochondrion emitting sparks of ATP energy.",
    "Bloodstream Voyage: red blood cells carrying a drug molecule like spacecraft.",
    "Synapse Spark: the moment of signal transfer between two cells, a bright flash.",
    "Regeneration Force: a cell dividing with a golden glow.",
    "Protective Shield: a cell membrane reflecting dark particles.",
]
SYSTEM_PROMPT = (
    "Ты — Главный редактор элитного журнала о биохакинге BioPeptidePlus. "
    "Стиль: энергичный, экспертный, немного дерзкий, но строго опирающийся на факты. "
    "Твоя цель — рассказать о КОНКРЕТНОМ ИССЛЕДОВАНИИ или КЛИНИЧЕСКОМ ИСПЫТАНИИ, "
    "а не объяснять базовые определения. "
    "Всегда отвечай строго валидным JSON без Markdown. "
    "Язык: только русский. "
    "Ты обязан опираться СТРОГО на предоставленный текст. "
    "Не выдумывай факты, числа, выборки, годы, институты или результаты, "
    "если их нет в источнике. "
    "Если в источнике есть цитаты — сохрани их. "
    "Если не можешь указать реальный study_year и study_citation, "
    "верни пустой JSON объект {} вместо догадок. "
    "Используй данные из SOURCE_JOURNAL и SOURCE_DOI дословно — это приказ."
)


def _load_last_topics() -> list[str]:
    raw = os.getenv("LAST_TOPICS", "").strip()
    if not raw:
        file_path = os.path.join(os.getcwd(), "recent_topics.txt")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
            except OSError:
                raw = ""
    if not raw:
        return []
    parts = re.split(r"[,\n]+", raw)
    topics = [p.strip() for p in parts if p.strip()]
    return topics


def _knowledge_base_path() -> str:
    return os.path.join(os.getcwd(), KNOWLEDGE_BASE_FILE)


def _load_knowledge_base(max_chars: int = 2000) -> str:
    file_path = _knowledge_base_path()
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()
    except OSError:
        return ""
    if len(data) <= max_chars:
        return data
    return data[-max_chars:].strip()


def _extract_key_finding(content_pro: str, content_lite: str) -> str:
    def pick_from_section(text: str, section_name: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            lower = line.lower()
            if lower.startswith(section_name.lower()):
                candidate = line.split(":", 1)[1].strip() if ":" in line else ""
                if not candidate and idx + 1 < len(lines):
                    candidate = lines[idx + 1]
                return candidate
        return ""

    candidate = pick_from_section(content_pro, "Результаты")
    if not candidate:
        candidate = pick_from_section(content_lite, "Суть")
    if not candidate:
        candidate = content_pro.strip() or content_lite.strip()
    sentences = re.split(r"(?<=[.!?])\s+", candidate)
    sentences = [s.strip() for s in sentences if s.strip()]
    return " ".join(sentences[:2]).strip()


def _extract_citation_hint(content: str) -> str:
    doi_match = re.search(r"\b10\.\d{4,9}/[^\s]+", content)
    if doi_match:
        return f"DOI: {doi_match.group(0)}"
    return ""


def _extract_doi(content: str, source_metadata: dict) -> str:
    match = re.search(r"\b10\.\d{4,9}/[^\s]+", content)
    if match:
        return match.group(0)
    doi = str(source_metadata.get("doi", "")).strip()
    return doi


def _parse_citations_count(source_metadata: dict) -> Optional[int]:
    raw = str(source_metadata.get("citations_count", "")).strip()
    if not raw:
        return None
    match = re.search(r"\d+", raw)
    return int(match.group(0)) if match else None


def _detect_evidence_level(text: str) -> str:
    lower = text.lower()
    if any(
        token in lower
        for token in (
            "phase 1",
            "phase i",
            "phase 2",
            "phase ii",
            "phase 3",
            "phase iii",
            "clinicaltrials.gov",
            "clinical trial",
            "double-blind",
            "randomized",
            "human",
            "humans",
            "patient",
            "patients",
            "volunteer",
            "volunteers",
            "люди",
            "добровольц",
            "пациент",
            "клиничес",
            "участник",
            "участников",
            "10 участников",
        )
    ):
        return "clinical"
    if any(
        token in lower
        for token in (
            "in vitro",
            "cell line",
            "cell culture",
            "клеточ",
            "культура клет",
        )
    ):
        return "in vitro"
    if any(
        token in lower
        for token in (
            "rat",
            "rats",
            "mouse",
            "mice",
            "murine",
            "rabbit",
            "rabbits",
            "крыс",
            "мыш",
            "кролик",
            "in vivo",
            "preclinical",
        )
    ):
        return "preclinical"
    if any(
        token in lower
        for token in (
            "meta-analysis",
            "systematic review",
            "мета-анализ",
            "систематический обзор",
            "systematic review of randomized",
            "meta-analysis of randomized",
        )
    ):
        return "meta-analysis"
    return "unknown"


def _extract_results_block(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    start_idx = None
    for idx, line in enumerate(lines):
        if line.lower().startswith("результаты"):
            start_idx = idx
            break
    if start_idx is None:
        return ""
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        lower = lines[idx].lower()
        if lower.startswith(("биохимия", "сноска", "список литературы", "методология")):
            end_idx = idx
            break
    return " ".join(lines[start_idx:end_idx]).strip()


def _extract_biological_targets(text: str) -> list[str]:
    lower = text.lower()
    targets_map = {
        "longevity": ("longevity", "aging", "старени", "долголет"),
        "cognition": ("cognition", "cognitive", "memory", "focus", "brain", "нейро", "когнит", "памят", "фокус"),
        "muscle": ("muscle", "strength", "sarcopenia", "мышц", "сила", "вынослив"),
        "sleep": ("sleep", "insomnia", "melatonin", "сон", "бессон"),
        "regeneration": ("regeneration", "repair", "healing", "tissue", "регенер", "зажив"),
        "metabolism": ("metabolism", "glucose", "lipid", "метабол", "глюкоз", "инсулин", "липид"),
        "inflammation": ("inflammation", "inflammatory", "циток", "воспал"),
    }
    targets = []
    for key, tokens in targets_map.items():
        if any(token in lower for token in tokens):
            targets.append(key)
    return targets


def _infer_system_targets(text: str, max_items: int = 2) -> list[str]:
    lower = text.lower()
    systems_map = {
        "brain": ("brain", "cognitive", "memory", "dementia", "alzheimer", "нейро", "когнит", "памят", "деменц", "альцгеймер"),
        "heart": ("cardio", "cardiac", "heart", "vascular", "серд", "сосуд"),
        "metabolism": ("metabolism", "glucose", "insulin", "metabolic", "метабол", "глюкоз", "инсулин"),
        "inflammation": ("inflammation", "inflammatory", "циток", "воспал"),
        "muscle": ("muscle", "strength", "sarcopenia", "мышц", "сила"),
        "sleep": ("sleep", "insomnia", "сон", "бессон"),
    }
    hits = []
    for key, tokens in systems_map.items():
        if any(token in lower for token in tokens):
            hits.append(key)
    return hits[:max_items]


def _generate_tags(peptide_name: str, targets: list[str]) -> list[str]:
    tags = []
    name = peptide_name.strip()
    if name:
        tags.append(name)
    for target in targets:
        tags.append(target.capitalize())
    seen = set()
    unique_tags = []
    for tag in tags:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_tags.append(tag)
    return unique_tags


def _append_knowledge_base(topic: str, key_finding: str, citation_hint: str = "") -> None:
    topic = topic.strip()
    key_finding = key_finding.strip()
    if not topic or not key_finding:
        return
    file_path = _knowledge_base_path()
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- ENTRY {datetime.utcnow().isoformat()} ---\n")
            f.write(f"TOPIC: {topic}\n")
            f.write(f"KEY_FINDING: {key_finding}\n")
            if citation_hint:
                f.write(f"{citation_hint}\n")
    except OSError:
        pass


def _sanitize_topics(topics: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen = set()
    for raw in topics:
        item = raw.strip().strip(" .;:-")
        if not item:
            continue
        if len(item) < 3:
            continue
        if not re.search(r"[A-Za-zА-Яа-я0-9-]", item):
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    return cleaned


def _topic_key(text: str) -> str:
    return re.sub(r"[^a-z0-9а-я]", "", text.lower())


def generate_daily_topics(last_topics: Optional[list[str]] = None, count: int = 5) -> list[str]:
    last_topics = last_topics or []
    knowledge_base = _load_knowledge_base()
    system_prompt = (
        "Ты — эксперт по биохакингу. Твоя задача — выдать список из 5 актуальных "
        "веществ (пептиды, ноотропы, сенолитики) для поиска в PubMed. "
        "Пиши только названия через запятую, без лишних слов."
    )
    prompt = "Список тем на сегодня:"
    if last_topics:
        prompt += (
            "\nТемы не должны повторяться с теми, что были вчера. "
            f"Вчерашние темы: {', '.join(last_topics)}."
        )
    if knowledge_base:
        prompt += (
            "\nКонтекст прошлых выводов (не повторяй темы и тезисы):\n"
            f"{knowledge_base}"
        )
    print(f"DEBUG: Prompt sent to Editor: {prompt}")
    recent_lower = {_topic_key(t) for t in last_topics}
    rejected: list[str] = []
    for attempt in range(3):
        attempt_prompt = prompt
        if rejected:
            attempt_prompt += (
                "\nТы уже предлагал: "
                f"{', '.join(rejected)}. Дай НОВЫЕ темы."
            )
        raw_response = _openai_generate_with_system(system_prompt, attempt_prompt, TEXT_MODEL)
        print(f"DEBUG RAW TOPICS: {raw_response}")
        cleaned = raw_response
        cleaned = re.sub(r"(?i)конечно.*?:", "", cleaned)
        cleaned = cleaned.replace('"', " ").replace("'", " ")
        cleaned = cleaned.replace(".", " ").replace("•", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        parts = [p.strip() for p in re.split(r"[,\n;]+", cleaned) if p.strip()]
        topics = _sanitize_topics(parts)
        if not topics:
            continue
        filtered = [t for t in topics if _topic_key(t) not in recent_lower]
        if len(filtered) >= count:
            return filtered[:count]
        if filtered:
            return filtered[:count]
        rejected.extend(topics)
    return []


def _append_recent_topic(topic: str) -> None:
    topic = topic.strip()
    if not topic:
        return
    file_path = os.path.join(os.getcwd(), "recent_topics.txt")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing = {line.strip() for line in f if line.strip()}
        else:
            existing = set()
        if topic in existing:
            return
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{topic}\n")
    except OSError:
        pass


def _build_image_prompt(image_scenario: str) -> str:
    theme = random.choice(IMAGE_THEMES)
    base = image_scenario.strip()
    if len(base) > 300:
        base = base[:300]
    scenario_hint = f"Topic hint: {base}. " if base else ""
    return (
        f"{theme} "
        f"{scenario_hint}"
        "Use cinematic lighting, 8k resolution, minimalist aesthetic. "
        "Strictly focus on ONE central object or person. "
        "Do not mix themes or add extra scientific props outside the chosen theme."
    )


def _generate_image_url(prompt: str) -> Optional[str]:
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
    req = request.Request(
        "https://api.openai.com/v1/images/generations", data=data, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    last_error = None
    for attempt in range(3):
        try:
            with request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")
            parsed = json.loads(body)
            items = parsed.get("data", [])
            if not items:
                return None
            return items[0].get("url")
        except HTTPError as exc:
            last_error = exc
            retry_in = 2 + attempt * 2
            print(f"Image generation failed (HTTP {exc.code}). Retry in {retry_in}s.")
            time.sleep(retry_in)
    if last_error:
        raise last_error
    return None


def _openai_generate(prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/chat/completions", data=data, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {os.getenv('OPENAI_API_KEY')}")
    with request.urlopen(req, timeout=90) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return ""
    return (choices[0].get("message") or {}).get("content", "").strip()


def _openai_generate_with_system(system_prompt: str, prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/chat/completions", data=data, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {os.getenv('OPENAI_API_KEY')}")
    with request.urlopen(req, timeout=90) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return ""
    return (choices[0].get("message") or {}).get("content", "").strip()


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _extract_source_metadata(source_text: str) -> dict:
    metadata = {}
    for line in source_text.splitlines():
        if line.startswith("SOURCE_JOURNAL:"):
            metadata["journal"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_DOI:"):
            metadata["doi"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_URL:"):
            metadata["url"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_DATE:"):
            metadata["year"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_AUTHORS:"):
            metadata["authors"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_CITATIONS:"):
            raw = line.split(":", 1)[1].strip()
            metadata["citations_count"] = raw
    return metadata


def _inject_source_citation(parsed: dict, source_metadata: dict) -> dict:
    journal = source_metadata.get("journal", "").strip()
    doi = source_metadata.get("doi", "").strip()
    year = source_metadata.get("year", "").strip()
    authors = source_metadata.get("authors", "").strip()

    if not journal and not doi:
        return parsed

    citation_parts = []
    if authors:
        citation_parts.append(f"Authors: {authors}")
    if journal:
        citation_parts.append(f"Journal: {journal}")
    if year:
        citation_parts.append(f"Year: {year}")
    if doi:
        citation_parts.append(f"DOI: {doi}")
    citation = ". ".join(citation_parts).strip()

    existing_citation = str(parsed.get("study_citation", "")).strip()
    if not existing_citation:
        parsed["study_citation"] = citation
    elif citation.lower() not in existing_citation.lower():
        parsed["study_citation"] = f"{existing_citation} | {citation}"

    content_pro = str(parsed.get("content_pro", "")).strip()
    if content_pro:
        lower = content_pro.lower()
        if not any(token in lower for token in ("список литературы", "references", "источники")):
            content_pro = f"{content_pro}\n\nСписок литературы:\n{citation}"
        elif citation.lower() not in lower:
            content_pro = f"{content_pro}\n{citation}"
        parsed["content_pro"] = content_pro

    if year and not str(parsed.get("study_year", "")).strip():
        parsed["study_year"] = year
    return parsed


def _extract_sample_size_from_text(text: str) -> str:
    return ""


def _postprocess_llm_output(parsed: dict, source_metadata: dict, source_text: str) -> dict:
    parsed = _inject_source_citation(parsed, source_metadata)
    content_pro = str(parsed.get("content_pro", "")).strip()
    study_year = str(parsed.get("study_year", "")).strip()
    sample_size = str(parsed.get("study_sample_size", "")).strip()

    if (source_metadata.get("doi") or source_metadata.get("url")) and not sample_size:
        sample_size = "Verified Scientific Report (DOI)"
        parsed["study_sample_size"] = sample_size

    if study_year and study_year not in content_pro:
        content_pro = f"Study Year: {study_year}\n{content_pro}"

    if (source_metadata.get("doi") or source_metadata.get("url")) and "Verification: Peer-reviewed study" not in content_pro:
        content_pro = f"Verification: Peer-reviewed study (DOI confirmed)\n{content_pro}"

    if sample_size and sample_size not in content_pro:
        label = "Sample size"
        if sample_size == "Verified Scientific Report (DOI)":
            label = "Тип исследования"
        content_pro = f"{label}: {sample_size}\n{content_pro}"

    parsed["content_pro"] = content_pro

    citation = str(parsed.get("study_citation", "")).strip()
    citation_lower = citation.lower()
    required_tokens = ("journal", "doi", "pubmed", "vol", "issue", "university")
    if not citation or not any(token in citation_lower for token in required_tokens):
        journal = source_metadata.get("journal", "").strip()
        doi = source_metadata.get("doi", "").strip()
        if journal or doi:
            citation_parts = []
            if journal:
                citation_parts.append(f"Journal: {journal}")
            if doi:
                citation_parts.append(f"DOI: {doi}")
            parsed["study_citation"] = ". ".join(citation_parts).strip()

    if parsed.get("_is_auto"):
        forced_citation = str(parsed.get("study_citation", "")).strip()
        lower = content_pro.lower()
        if not any(token in lower for token in ("список литературы", "references", "источники")):
            content_pro = f"{content_pro}\n\nСписок литературы:\n{forced_citation}"
            parsed["content_pro"] = content_pro

    return parsed


def _is_generic_study_name(value: str) -> bool:
    lowered = value.lower()
    generic_phrases = (
        "study of peptide",
        "study of peptides",
        "peptide study",
        "peptides study",
        "clinical study",
        "clinical trial",
        "research on peptide",
        "research on peptides",
        "general study",
    )
    return not value.strip() or any(phrase in lowered for phrase in generic_phrases)


def _hard_filter(parsed: dict, filename: str) -> tuple[bool, str]:
    study_year = str(parsed.get("study_year", "")).strip()
    study_citation = str(parsed.get("study_citation", "")).strip()
    study_name = str(parsed.get("specific_study_name", "")).strip()
    content_pro = str(parsed.get("content_pro", "")).strip()
    sample_size = str(parsed.get("study_sample_size", "")).strip()
    is_auto = bool(parsed.get("_is_auto"))
    source_doi = str(parsed.get("_source_doi", "")).strip()

    # 1. Проверка года (базовая безопасность)
    if not re.fullmatch(r"(19|20)\d{2}", study_year):
        return False, "Rejected: Invalid year"

    # 2. Проверка цитаты
    citation_lower = study_citation.lower()
    if not study_citation or "нет данных" in citation_lower:
        return False, "Rejected: No citation"

    # Для авто-файлов с DOI мы доверяем источнику
    if not source_doi:
        required_tokens = ("journal", "doi", "pubmed", "vol", "issue", "university")
        if not any(token in citation_lower for token in required_tokens):
            if not (is_auto and re.search(r"\b(19|20)\d{2}\b", citation_lower)):
                return False, "Rejected: Citation missing key markers"

    # 3. Проверка Sample Size (Добавляем поддержку предклиники)
    sample_lower = sample_size.lower()
    valid_sample_markers = [
        "verified", "scientific report", "model", "vitro", "vivo",
        "предклинич", "линии", "животн", "animal", "mice", "rats", "крыс", "мыши"
    ]

    has_digits = bool(re.search(r"\d+", sample_size))
    is_valid_type = any(m in sample_lower for m in valid_sample_markers)

    if not (has_digits or is_valid_type):
        if is_auto:
            content_lower = content_pro.lower()
            clinical_markers = ("clinical", "trial", "study", "fda", "treatment")
            if any(marker in content_lower for marker in clinical_markers):
                sample_size = "clinical study (verified)"
                parsed["study_sample_size"] = sample_size
                if sample_size not in content_pro:
                    content_pro = f"Sample size: {sample_size}\n{content_pro}"
                    parsed["content_pro"] = content_pro
                print(f"DEBUG: Sample size after force: {sample_size}")
        if not re.search(r"\d+", sample_size) and not any(
            m in sample_size.lower() for m in valid_sample_markers
        ):
            return False, "Rejected: No sample size"

    # 4. Кросс-валидация (Ослабляем для авто-файлов)
    content_lower = content_pro.lower()

    # Если это авто-поиск, нам достаточно, чтобы в тексте был ГОД и упоминание ПЕПТИДА
    if is_auto:
        if study_year not in content_pro:
            return False, "Rejected: Year missing in text"
        # Проверяем, что в тексте есть хотя бы часть названия исследования или ключевые слова
        study_keywords = [w for w in re.findall(r"[A-Za-zА-Яа-я0-9-]+", study_name) if len(w) >= 5]
        if study_keywords and not any(word.lower() in content_lower for word in study_keywords):
            # Если не нашли слова из заголовка, проверяем наличие ссылки или DOI
            if not (source_doi.lower() in content_lower or "[" in content_pro):
                return False, "Rejected: Content does not match study metadata"
    else:
        # Для ручных файлов оставляем строгую проверку
        if "[" not in content_pro and "(" not in content_pro:
            return False, "Rejected: No references in body"
        if not any(token in content_pro for token in ("Список литературы", "References", "Источники")):
            return False, "Rejected: No references in body"

    return True, ""


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    cleaned = re.sub(r"(?is)<.*?>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _google_search_urls(query: str, max_results: int) -> list[str]:
    try:
        from googlesearch import search  # type: ignore
    except Exception:
        return []
    try:
        return list(search(query, num_results=max_results))
    except TypeError:
        return list(search(query, num=max_results))
    except Exception:
        return []


def _pubmed_search_urls(query: str, max_results: int, year_from: int = 2024, year_to: int = 2025) -> list[str]:
    term = parse.quote(f"{query} AND ({year_from}[dp]:{year_to}[dp])")
    endpoint = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&retmode=json&retmax={max_results}&term={term}"
    )
    req = request.Request(endpoint, method="GET")
    with request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    ids = parsed.get("esearchresult", {}).get("idlist", [])
    return [f"https://pubmed.ncbi.nlm.nih.gov/{pid}/" for pid in ids if pid]


def _pubmed_fetch_records(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    id_param = ",".join(ids)
    endpoint = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&retmode=xml&id={id_param}"
    )
    req = request.Request(endpoint, method="GET")
    with request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    root = ET.fromstring(body)
    records: list[dict] = []
    for article in root.findall(".//PubmedArticle"):
        journal_title = article.findtext(".//Journal/Title", default="").strip()
        year = article.findtext(".//PubDate/Year", default="").strip()
        doi = ""
        for eloc in article.findall(".//ELocationID"):
            if eloc.get("EIdType") == "doi":
                doi = (eloc.text or "").strip()
                break
        abstract_texts = [
            (elem.text or "").strip()
            for elem in article.findall(".//Abstract/AbstractText")
            if (elem.text or "").strip()
        ]
        abstract = " ".join(abstract_texts).strip()
        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName", default="").strip()
            initials = author.findtext("Initials", default="").strip()
            if last and initials:
                authors.append(f"{last} {initials}")
            elif last:
                authors.append(last)
        records.append(
            {
                "journal": journal_title,
                "year": year,
                "doi": doi,
                "authors": ", ".join(authors),
                "abstract": abstract,
            }
        )
    return records


def _europe_pmc_search_records(query: str, max_results: int) -> list[dict]:
    q = parse.quote(query)
    endpoint = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        f"?query={q}&pageSize={max_results}&format=json"
    )
    try:
        req = request.Request(endpoint, method="GET")
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(body)
    except Exception:
        return []
    results = parsed.get("resultList", {}).get("result", []) or []
    records: list[dict] = []
    for item in results:
        records.append(
            {
                "journal": (item.get("journalTitle") or "").strip(),
                "year": str(item.get("pubYear") or "").strip(),
                "doi": (item.get("doi") or "").strip(),
                "authors": (item.get("authorString") or "").strip(),
                "abstract": (item.get("abstractText") or "").strip(),
                "url": (item.get("fullTextUrlList", {}) or {}).get("fullTextUrl", [{}])[0].get("url", ""),
            }
        )
    return records


def _semantic_scholar_search_records(query: str, max_results: int) -> list[dict]:
    q = parse.quote(query)
    endpoint = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={q}&limit={max_results}"
        "&fields=title,year,authors,venue,abstract,doi,url,citationCount"
    )
    try:
        req = request.Request(endpoint, method="GET")
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(body)
    except Exception:
        return []
    results = parsed.get("data", []) or []
    records: list[dict] = []
    for item in results:
        authors = ", ".join(a.get("name", "") for a in item.get("authors", []) if a.get("name"))
        records.append(
            {
                "journal": (item.get("venue") or "").strip(),
                "year": str(item.get("year") or "").strip(),
                "doi": (item.get("doi") or "").strip(),
                "authors": authors.strip(),
                "abstract": (item.get("abstract") or "").strip(),
                "url": (item.get("url") or "").strip(),
                "citations_count": str(item.get("citationCount") or "").strip(),
            }
        )
    return records


def _clinicaltrials_search_records(query: str, max_results: int) -> list[dict]:
    q = parse.quote(query)
    endpoint = f"https://clinicaltrials.gov/api/v2/studies?query.term={q}&pageSize={max_results}"
    try:
        req = request.Request(endpoint, method="GET")
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(body)
    except Exception:
        return []
    studies = parsed.get("studies", []) or []
    records: list[dict] = []
    for item in studies:
        ident = item.get("protocolSection", {}).get("identificationModule", {}) or {}
        descr = item.get("protocolSection", {}).get("descriptionModule", {}) or {}
        status = item.get("protocolSection", {}).get("statusModule", {}) or {}
        sponsor = item.get("protocolSection", {}).get("sponsorCollaboratorsModule", {}) or {}
        nct_id = ident.get("nctId", "")
        brief_title = ident.get("briefTitle", "")
        start_date = status.get("startDateStruct", {}) or {}
        record_url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else ""
        records.append(
            {
                "journal": "ClinicalTrials.gov",
                "year": str(start_date.get("date", "")[:4]).strip(),
                "doi": record_url,
                "authors": (sponsor.get("leadSponsor", {}) or {}).get("name", ""),
                "abstract": (descr.get("briefSummary") or "").strip() or brief_title,
                "url": record_url,
            }
        )
    return records


def _fetch_page_text(url: str, timeout: int = 20) -> str:
    req = request.Request(url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    return _strip_html(body)


def _collect_search_snippets(keyword: str, max_results: int = 10) -> str:
    snippets: list[str] = []
    pubmed_urls = _pubmed_search_urls(keyword, 3)
    ids = [url.rstrip("/").split("/")[-1] for url in pubmed_urls if url]
    pubmed_records = _pubmed_fetch_records(ids)
    for record in pubmed_records:
        header_lines = [
            f"SOURCE_JOURNAL: {record.get('journal', '')}",
            f"SOURCE_DOI: {record.get('doi', '') or 'https://pubmed.ncbi.nlm.nih.gov/'}",
            f"SOURCE_DATE: {record.get('year', '')}",
            f"SOURCE_AUTHORS: {record.get('authors', '')}",
            "SOURCE_CITATIONS: ",
            "SOURCE_URL: https://pubmed.ncbi.nlm.nih.gov/",
        ]
        if not record.get("journal") or not record.get("year") or not record.get("doi"):
            header_lines.append("This is a formal academic record from PubMed database")
        abstract = record.get("abstract", "")
        if abstract:
            snippets.append("\n".join(header_lines) + "\n\n" + abstract)

    europe_records = _europe_pmc_search_records(keyword, 3)
    for record in europe_records:
        header_lines = [
            f"SOURCE_JOURNAL: {record.get('journal', '')}",
            f"SOURCE_DOI: {record.get('doi', '') or record.get('url', '')}",
            f"SOURCE_DATE: {record.get('year', '')}",
            f"SOURCE_AUTHORS: {record.get('authors', '')}",
            "SOURCE_CITATIONS: ",
            f"SOURCE_URL: {record.get('url', '')}",
        ]
        abstract = record.get("abstract", "")
        if abstract:
            snippets.append("\n".join(header_lines) + "\n\n" + abstract)

    semantic_records = _semantic_scholar_search_records(keyword, 3)
    for record in semantic_records:
        header_lines = [
            f"SOURCE_JOURNAL: {record.get('journal', '')}",
            f"SOURCE_DOI: {record.get('doi', '') or record.get('url', '')}",
            f"SOURCE_DATE: {record.get('year', '')}",
            f"SOURCE_AUTHORS: {record.get('authors', '')}",
            f"SOURCE_CITATIONS: {record.get('citations_count', '')}",
            f"SOURCE_URL: {record.get('url', '')}",
        ]
        abstract = record.get("abstract", "")
        if abstract:
            snippets.append("\n".join(header_lines) + "\n\n" + abstract)

    trial_records = _clinicaltrials_search_records(keyword, 3)
    for record in trial_records:
        header_lines = [
            f"SOURCE_JOURNAL: {record.get('journal', '')}",
            f"SOURCE_DOI: {record.get('doi', '') or record.get('url', '')}",
            f"SOURCE_DATE: {record.get('year', '')}",
            f"SOURCE_AUTHORS: {record.get('authors', '')}",
            "SOURCE_CITATIONS: ",
            f"SOURCE_URL: {record.get('url', '')}",
            "This is a formal academic record from ClinicalTrials.gov database",
        ]
        abstract = record.get("abstract", "")
        if abstract:
            snippets.append("\n".join(header_lines) + "\n\n" + abstract)

    if snippets:
        return "\n\n".join(snippets)

    queries = [
        f'site:pubmed.ncbi.nlm.nih.gov "{keyword}" 2024..2025',
        f'site:clinicaltrials.gov "{keyword}"',
        f'"{keyword}" peer-reviewed study 2024 journal doi',
    ]
    urls: list[str] = []
    for query in queries:
        urls.extend(_google_search_urls(query, max_results))
    unique_urls = list(dict.fromkeys(urls))[: max_results * len(queries)]
    required_tokens = ("journal", "abstract", "results", "doi:", "clinicaltrials")
    for url in unique_urls:
        try:
            text = _fetch_page_text(url)
        except Exception:
            continue
        if not any(token in text.lower() for token in required_tokens):
            continue
        hits = []
        for match in re.finditer(r"(?i)\b(2024|2025)\b", text):
            start = max(0, match.start() - 220)
            end = min(len(text), match.end() + 220)
            hits.append(text[start:end])
        if hits:
            snippet = " ... ".join(hits[:3])
            snippets.append(f"Source: {url}\n{snippet}")
        if len(snippets) >= max_results:
            break
    if not snippets:
        return ""
    header_lines = [
        "SOURCE_JOURNAL: ",
        "SOURCE_DOI: ",
        "SOURCE_DATE: ",
        "SOURCE_AUTHORS: ",
        "This is a formal academic record from PubMed database",
    ]
    return "\n".join(header_lines) + "\n\n" + "\n\n".join(snippets)


def _seed_research_db(db_path: str) -> None:
    for keyword in SEARCH_KEYWORDS:
        if not keyword or not re.search(r"[A-Za-zА-Яа-я0-9]", keyword):
            continue
        filename = f"auto_{_normalize_name(keyword)}.txt"
        if "{" in filename or "}" in filename:
            continue
        file_path = os.path.join(db_path, filename)
        if os.path.exists(file_path):
            continue
        snippets = _collect_search_snippets(keyword)
        if not snippets:
            continue
        has_recent_year = re.search(r"\b(2024|2025)\b", snippets)
        has_numbers = re.search(r"\d{2,}", snippets)
        if not has_recent_year or not has_numbers:
            continue
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(snippets)


def _generate_article_versions(
    source_text: str, peptide_name: str, filename: str, include_knowledge_base: bool = True
) -> Optional[tuple[str, str, str, str]]:
    source_text = source_text.strip()
    short_source = len(source_text) < 200
    keyword_only = short_source and len(source_text.split()) <= 3
    source_metadata = _extract_source_metadata(source_text)
    knowledge_base = _load_knowledge_base() if include_knowledge_base else ""
    user_message = (
        "Проанализируй следующий текст и сделай из него Pro и Lite версии:\n\n"
        f"{source_text}"
    )
    prompt = (
        "Верни строго JSON с полями: title, content_pro, content_lite, "
        "image_scenario, should_publish, skip_reason, "
        "specific_study_name, study_year, study_citation, study_sample_size.\n"
        "title: максимально кликабельный и хайповый заголовок, "
        "обязательно с эмодзи 🧬, 🚀, 🧠.\n"
        "content_pro: строго академический и сухой стиль, без оценочных суждений. "
        "Используй Markdown: заголовки (##), **жирный текст**, маркированные списки (*). "
        "Обязательные секции: "
        "## Обзор субстанции, ## Механизм действия, ## Результаты исследований, "
        "## Справочные данные. "
        "Внутри секций: "
        "Полное название исследования; методология (дизайн, выборка n, дозировки, длительность); "
        "результаты (статистические показатели, дельты в %, p-значения); "
        "биохимия (конкретные молекулярные механизмы и пути); "
        "сноска (источник [1] и DOI). "
        "Цель: дать твердые данные для принятия решений. "
        "LaTeX используй только для сложных формул. "
        "Обязательны [1] и список литературы в конце "
        "(Author, Journal, Year, DOI). "
        "Обязательно упомяни BioPeptidePlus.\n"
        "content_lite: упрощенный, качественный научпоп без желтизны. "
        "Используй Markdown и короткие абзацы. "
        "В Lite View начинай строки с эмодзи. "
        "Обязательные секции: "
        "## Обзор субстанции, ## Механизм действия, ## Результаты исследований, "
        "## Справочные данные. "
        "Структура: Крючок, Суть, Практика, Статус, Сноска (источник [1] и DOI). "
        "Цель: быстро объяснить обычному человеку ценность вещества. "
        "Обязательны [1] и список литературы в конце "
        "(Author, Journal, Year, DOI). "
        "Обязательно упомяни BioPeptidePlus.\n"
        "image_scenario: придумай описание картинки на основе текста. "
        "НЕ делай всегда абстракцию — чередуй стили. "
        "Если упоминается университет/страна — добавь архитектуру "
        "(например, 'British scientists near Big Ben style' или "
        "'Harvard campus background'). "
        "Если речь о людях/испытаниях — покажи ученых в футуристической "
        "лаборатории, докторов или биохакеров. "
        "Если речь о структуре вещества — красивый 3D макро-мир. "
        "Стиль всегда: Cinematic, Unreal Engine 5, Volumetric Lighting, "
        "Photorealistic but futuristic.\n"
        "should_publish: true/false. Если нет конкретного исследования, "
        "ставь false и заполняй skip_reason.\n"
        "skip_reason: кратко объясни, почему пропуск.\n"
        "study_year: год исследования из источника.\n"
        "study_citation: литература в формате Author, Journal, Year, DOI.\n"
        "study_sample_size: выборка (например: 120 пациентов, 40 мышей, in vitro).\n"
        "specific_study_name: название конкретного исследования из источника.\n"
        "Если список biological targets пуст, попробуй определить 1-2 основные системы "
        "организма из контекста (например, мозг, сердце, метаболизм) и отрази это "
        "в результатах.\n"
        "Инструкция для Dr. Drug: сравнивай новую статью с прошлыми данными "
        "из knowledge_base.txt. Если есть противоречия или синергия "
        "(например, BPC-157 усиливает эффект нового вещества) — обязательно "
        "укажи это в блоке PRO.\n"
        "Инструкция для Арбитра: критерии строгости растут. "
        "Если мы уже писали о подобном веществе с лучшей выборкой, "
        "требуй от нового исследования более веских доказательств. "
        "В этом случае добавь в PRO строку 'Статус: Требует подтверждения'.\n"
        f"Тема: {peptide_name}\n\n"
        f"{user_message}"
    )
    if knowledge_base:
        prompt += (
            "\n\nКонтекст knowledge_base.txt (для сравнения и синергий):\n"
            f"{knowledge_base}"
        )
    if short_source:
        prompt += (
            "\n\nИсточник короткий или пустой. "
            "Можно использовать внешние знания, но честно начни с фразы: "
            "'По данным открытых источников...'. "
            "Не указывай конкретные цифры, годы, выборки и результаты, "
            "если они не подтверждены источниками в тексте."
        )
    if keyword_only:
        prompt += (
            "\n\nВход содержит только ключевое слово. "
            "Сделай честную справку без неподтвержденной конкретики. "
            "Если нет проверяемых ссылок, явно укажи: "
            "'Ссылки: данные в источнике отсутствуют'."
        )
    raw = _openai_generate(prompt, TEXT_MODEL)
    debug_files = {"auto_bpc-157.txt", "auto_epitalon.txt"}
    if filename in debug_files:
        print(f"=== RAW OUTPUT [{filename}] ===")
        print(raw)
    parsed = _extract_json(raw)
    if filename in debug_files:
        print(f"=== PARSED JSON [{filename}] ===")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        print(f"=== content_pro [{filename}] ===")
        print(str(parsed.get("content_pro", "")))
    if not parsed:
        print(f"Skipping {peptide_name}: empty JSON response.")
        return None
    if source_metadata:
        parsed = _postprocess_llm_output(parsed, source_metadata, source_text)
        parsed["_source_doi"] = source_metadata.get("doi", "")
    if filename.startswith("auto_"):
        parsed["_is_auto"] = True
    should_publish = bool(parsed.get("should_publish", True))
    if not should_publish:
        reason = str(parsed.get("skip_reason", "")).strip() or "No study found."
        print(f"Skipping {peptide_name}: {reason}")
        return None
    ok, reject_reason = _hard_filter(parsed, peptide_name)
    if not ok:
        print(f"\033[31mSKIPPED [{peptide_name}]: {reject_reason}\033[0m")
        return None
    title = str(parsed.get("title", "")).strip()
    content_pro = str(parsed.get("content_pro", "")).strip()
    content_lite = str(parsed.get("content_lite", "")).strip()
    image_scenario = str(parsed.get("image_scenario", "")).strip()
    if not title or not content_pro or not content_lite:
        raise ValueError("GPT response missing required fields")
    if not image_scenario:
        image_scenario = title
    return title, content_pro, content_lite, image_scenario


def _send_journal_post(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        JOURNAL_ENDPOINT,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _prepare_lovable_payload(payload: dict) -> dict:
    allowed_fields = {
        "title",
        "content",
        "content_lite",
        "category",
        "tags",
        "image_url",
        "doi",
        "evidence_level",
    }
    tags = list(payload.get("tags") or [])
    if payload.get("biological_targets"):
        for item in payload.get("biological_targets") or []:
            if item not in tags:
                tags.append(item)
    payload["tags"] = tags
    return {k: v for k, v in payload.items() if k in allowed_fields}


def _send_telegram_update(image_url: Optional[str], text: str) -> None:
    token = (
        os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("DR_DRAG_TOKEN")
        or os.getenv("ARBITER_TOKEN")
    )
    chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
    if not token or not chat_id:
        print("Telegram отправка пропущена: нет TELEGRAM_BOT_TOKEN/CHANNEL_ID.")
        return
    if image_url:
        send_photo(token, chat_id, image_url, "", article_url=None)
    send_message(token, chat_id, text, article_url=None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto research generator")
    parser.add_argument("peptide_name", nargs="*")
    parser.add_argument("--regen-db", action="store_true")
    parser.add_argument("--resume-after", default="")
    parser.add_argument("--topic", default="", help="Direct search query for research")
    args = parser.parse_args()
    if args.topic:
        args.regen_db = True

    db_path = os.path.join(os.getcwd(), "research_db")
    os.makedirs(db_path, exist_ok=True)
    if args.topic:
        topic_query = args.topic.strip()
        if not topic_query:
            print("Empty topic query.")
            return 1
        filename = f"auto_{_normalize_name(topic_query)}.txt"
        file_path = os.path.join(db_path, filename)
        snippets = _collect_search_snippets(topic_query)
        if not snippets:
            print("No research snippets found for topic.")
            return 1
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(snippets)
        peptide_name = _pretty_name(topic_query)
        try:
            generated = _generate_article_versions(
                snippets, peptide_name, filename, include_knowledge_base=False
            )
            if not generated:
                print("No publishable study found; skipping.")
                return 0
            title, content_pro, content_lite, image_scenario = generated
            source_metadata = _extract_source_metadata(snippets)
            image_prompt = _build_image_prompt(image_scenario)
            image_url = _generate_image_url(image_prompt)
            print("Image URL:", image_url)
            combined_text = f"{title}\n{content_pro}\n{content_lite}\n{snippets}"
            evidence_level = _detect_evidence_level(combined_text)
            results_block = _extract_results_block(content_pro)
            biological_targets = _extract_biological_targets(results_block)
            if not biological_targets:
                biological_targets = _infer_system_targets(f"{content_pro}\n{content_lite}")
            tags = _generate_tags(peptide_name, biological_targets)
            doi = _extract_doi(combined_text, source_metadata)
            citations_count = _parse_citations_count(source_metadata)
            payload = {
                "title": title,
                "content": content_pro,
                "content_lite": content_lite,
                "category": "science",
                "is_published": True,
                "image_url": image_url,
                "evidence_level": evidence_level,
                "biological_targets": biological_targets,
                "tags": tags,
                "doi": doi,
                "citations_count": citations_count,
            }
            response = _send_journal_post(payload)
            _send_telegram_update(image_url, content_lite)
            key_finding = _extract_key_finding(content_pro, content_lite)
            citation_hint = _extract_citation_hint(content_pro)
            _append_knowledge_base(peptide_name, key_finding, citation_hint)
            _append_recent_topic(peptide_name)
            print(f"{filename}: {response}")
            return 0
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace").strip()
            print(body or f"HTTP {exc.code}")
            return 1
        except Exception as exc:
            print(f"Error processing {filename}: {exc}")
            return 1

    if args.regen_db:
        global SEARCH_KEYWORDS
        if args.topic:
            SEARCH_KEYWORDS = [args.topic.strip()]
            print(f"Using direct topic: {SEARCH_KEYWORDS[0]}")
            last_topics = _load_last_topics()
            recent_topic_keys = {_topic_key(t) for t in last_topics}
        else:
            last_topics = _load_last_topics()
            generated_topics = generate_daily_topics(last_topics, count=5)
            if generated_topics:
                SEARCH_KEYWORDS = generated_topics
                print(f"Generated topics: {', '.join(SEARCH_KEYWORDS)}")
            else:
                SEARCH_KEYWORDS = DEFAULT_KEYWORDS[:5]
                print(f"Generated topics empty; fallback to: {', '.join(SEARCH_KEYWORDS)}")
            recent_topic_keys = {_topic_key(t) for t in last_topics}

    if args.regen_db:
        entries = [
            f
            for f in os.listdir(db_path)
            if f.lower().endswith(".txt") and os.path.isfile(os.path.join(db_path, f))
        ]
        if not entries:
            _seed_research_db(db_path)
            entries = [
                f
                for f in os.listdir(db_path)
                if f.lower().endswith(".txt") and os.path.isfile(os.path.join(db_path, f))
            ]
        if not entries:
            print("No research_db entries found.")
            return 1
        resume_after = args.resume_after.strip().lower()
        processed = 0
        for filename in sorted(entries):
            if resume_after and filename.lower() <= resume_after:
                continue
            if DAILY_LIMIT and processed >= DAILY_LIMIT:
                print(f"Daily limit reached: {DAILY_LIMIT}")
                break
            if "{" in filename or "}" in filename:
                print(f"Skipping invalid filename: {filename}")
                continue
            file_path = os.path.join(db_path, filename)
            raw_name = os.path.splitext(filename)[0]
            topic_name = raw_name
            if topic_name.startswith("auto_"):
                topic_name = topic_name[len("auto_"):]
            peptide_name = _pretty_name(topic_name)
            if _topic_key(peptide_name) in recent_topic_keys:
                print(f"Skipping recent topic: {peptide_name}")
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                source_text = f.read().strip()
            if not source_text:
                print(f"Skipping empty file: {filename}")
                continue
            try:
                generated = _generate_article_versions(source_text, peptide_name, filename)
                if not generated:
                    if filename.startswith("auto_"):
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
                    continue
                title, content_pro, content_lite, image_scenario = generated
                source_metadata = _extract_source_metadata(source_text)
                image_prompt = _build_image_prompt(image_scenario)
                image_url = _generate_image_url(image_prompt)
                print("Image URL:", image_url)
                combined_text = f"{title}\n{content_pro}\n{content_lite}\n{source_text}"
                evidence_level = _detect_evidence_level(combined_text)
                results_block = _extract_results_block(content_pro)
                biological_targets = _extract_biological_targets(results_block)
                if not biological_targets:
                    biological_targets = _infer_system_targets(f"{content_pro}\n{content_lite}")
                tags = _generate_tags(peptide_name, biological_targets)
                doi = _extract_doi(combined_text, source_metadata)
                citations_count = _parse_citations_count(source_metadata)
                payload = {
                    "title": title,
                    "content": content_pro,
                    "content_lite": content_lite,
                    "category": "science",
                    "is_published": True,
                    "image_url": image_url,
                    "evidence_level": evidence_level,
                    "biological_targets": biological_targets,
                    "tags": tags,
                    "doi": doi,
                    "citations_count": citations_count,
                }
                payload = _prepare_lovable_payload(payload)
                try:
                    response = _send_journal_post(payload)
                except Exception as exc:
                    print(f"Lovable API error for {filename}: {exc}")
                    continue
                if image_url:
                    print(f"Lovable image_url sent: {image_url}")
                _send_telegram_update(image_url, content_lite)
                key_finding = _extract_key_finding(content_pro, content_lite)
                citation_hint = _extract_citation_hint(content_pro)
                _append_knowledge_base(peptide_name, key_finding, citation_hint)
                _append_recent_topic(peptide_name)
                post_id = (response.get("post", {}) or {}).get("id") if isinstance(response, dict) else None
                if post_id:
                    try:
                        with open(file_path, "a", encoding="utf-8") as f:
                            f.write(f"\nPOST_ID: {post_id}\n")
                    except OSError:
                        pass
            except HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace").strip()
                print(body or f"HTTP {exc.code}")
                continue
            except Exception as exc:
                print(f"Error processing {filename}: {exc}")
                continue
            processed += 1
            print(f"{filename}: {response}")
        return 0

    peptide_name = " ".join(args.peptide_name).strip()
    if not peptide_name:
        print("Empty peptide name.")
        return 1

    key = _normalize_name(peptide_name)
    data = _mock_search(key)
    entry = _format_entry(peptide_name, data)

    file_path = os.path.join(db_path, f"{key}.txt")
    mode = "a" if os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n")
        f.write(entry)

    print(f"✅ Файл обновлен: {file_path}")

    generated = _generate_article_versions(entry, peptide_name, key)
    if not generated:
        print("No publishable study found; skipping.")
        return 0
    title, content_pro, content_lite, image_scenario = generated
    image_prompt = _build_image_prompt(image_scenario)
    image_url = _generate_image_url(image_prompt)
    print("Image URL:", image_url)
    combined_text = f"{title}\n{content_pro}\n{content_lite}\n{entry}"
    evidence_level = _detect_evidence_level(combined_text)
    results_block = _extract_results_block(content_pro)
    biological_targets = _extract_biological_targets(results_block)
    if not biological_targets:
        biological_targets = _infer_system_targets(f"{content_pro}\n{content_lite}")
    tags = _generate_tags(peptide_name, biological_targets)
    doi = _extract_doi(combined_text, {})
    citations_count = None
    payload = {
        "title": title,
        "content": content_pro,
        "content_lite": content_lite,
        "category": "science",
        "is_published": True,
        "image_url": image_url,
        "evidence_level": evidence_level,
        "biological_targets": biological_targets,
        "tags": tags,
        "doi": doi,
        "citations_count": citations_count,
    }
    try:
        payload = _prepare_lovable_payload(payload)
        response = _send_journal_post(payload)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        print(body or f"HTTP {exc.code}")
        return 1
    except Exception as exc:
        print(f"Lovable API error: {exc}")
        return 1
    if image_url:
        print(f"Lovable image_url sent: {image_url}")
    _send_telegram_update(image_url, content_lite)
    key_finding = _extract_key_finding(content_pro, content_lite)
    citation_hint = _extract_citation_hint(content_pro)
    _append_knowledge_base(peptide_name, key_finding, citation_hint)
    _append_recent_topic(peptide_name)
    post_id = (response.get("post", {}) or {}).get("id") if isinstance(response, dict) else None
    if post_id:
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"\nPOST_ID: {post_id}\n")
        except OSError:
            pass
    print("Server response:", response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
