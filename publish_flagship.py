import os
from dotenv import load_dotenv
from supabase import create_client, Client

import research_auto_ai as r


def main() -> None:
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_ANON_KEY")

    supabase: Client = create_client(supabase_url, supabase_key)

    payload = {
        "title": "BPC-157: Механизмы модуляции ангиогенеза и системной цитопротекции",
        "content": (
            "BPC-157 (Body Protection Compound-157) — синтетический "
            "пентадекапептид, производный от защитного белка желудочного сока. "
            "Основной биологический эффект связан со стимуляцией ангиогенеза "
            "через активацию VEGF. В доклинических моделях демонстрирует "
            "ускорение заживления связок, сухожилий и слизистой ЖКТ. "
            "Субстанция предназначена исключительно для лабораторных исследований."
        ),
        "content_lite": "",
        "category": "peptide",
        "tags": ["regeneration", "inflammation"],
        "evidence_level": "preclinical",
        "doi": "10.2174/138161210790883559",
        "image_url": None,
    }

    payload = r._prepare_lovable_payload(payload)
    response = None
    for _ in range(5):
        try:
            response = supabase.table("journal_posts").insert(payload).execute()
            break
        except Exception as exc:
            message = str(exc)
            if "Could not find the '" in message and "' column" in message:
                missing = message.split("Could not find the '", 1)[1].split("' column", 1)[0]
                payload.pop(missing, None)
                continue
            raise
    if response is None:
        raise RuntimeError("Insert failed after removing missing columns")
    data = response.data or []
    if not data:
        raise RuntimeError("Insert failed: no data returned")
    post_id = data[0].get("id", "")
    print(f"Inserted journal_posts row: {post_id or data[0]}")


if __name__ == "__main__":
    main()
