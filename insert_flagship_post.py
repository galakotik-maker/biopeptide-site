import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

active_key = SUPABASE_ANON_KEY or SUPABASE_KEY
if not SUPABASE_URL or not active_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, active_key)


def main() -> None:
    payload = {
        "title": "BPC-157: Механизмы модуляции ангиогенеза и системной цитопротекции",
        "category": "peptide",
        "evidence_level": "preclinical",
        "biological_targets": ["regeneration", "inflammation"],
        "doi": "10.2174/138161210790883559",
        "is_published": True,
        "content": (
            "BPC-157 (Body Protection Compound-157) — синтетический "
            "пентадекапептид, производный от защитного белка желудочного сока. "
            "Основной биологический эффект связан со стимуляцией ангиогенеза "
            "через активацию фактора роста эндотелия сосудов (VEGF). "
            "В доклинических моделях демонстрирует ускорение заживления связок, "
            "сухожилий и слизистой ЖКТ. Молекулярная масса: 1419.5 г/моль. "
            "Субстанция предназначена исключительно для лабораторных исследований."
        ),
    }

    response = supabase.table("journal_posts").insert(payload).execute()
    data = response.data or []
    if not data:
        raise RuntimeError("Insert failed: no data returned")
    post_id = data[0].get("id", "")
    print(f"Inserted research_posts row: {post_id or data[0]}")


if __name__ == "__main__":
    main()
