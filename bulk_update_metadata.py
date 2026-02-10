import os
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

MAPPING = {
    "biological_targets": {
        "мозг": "brain",
        "память": "brain",
        "когнитив": "brain",
        "нейро": "brain",
        "сердце": "heart",
        "сосуд": "heart",
        "кардио": "heart",
        "мышцы": "muscle",
        "сила": "muscle",
        "ткани": "muscle",
        "долголетие": "longevity",
        "старение": "longevity",
        "антиэйдж": "longevity",
        "регенерация": "regeneration",
        "заживление": "regeneration",
        "травм": "regeneration",
        "воспаление": "inflammation",
        "иммун": "inflammation",
    },
    "categories": {
        "пептид": "peptide",
        "нутрицевтик": "nutraceutical",
        "бад": "nutraceutical",
        "витамин": "nutraceutical",
        "биохакинг": "biohacking",
        "оптимизация": "biohacking",
    },
    "evidence": {
        "клиническое": "clinical",
        "людях": "clinical",
        "пациент": "clinical",
        "доклиник": "preclinical",
        "мышах": "preclinical",
        "крысах": "preclinical",
        "in vitro": "preclinical",
    },
}


def analyze_and_update_optimized(batch_size: int = 100) -> None:
    while True:
        response = (
            supabase.table("research_posts")
            .select("*")
            .or_("evidence_level.is.null,biological_targets.is.null")
            .limit(batch_size)
            .execute()
        )
        posts = response.data or []
        if not posts:
            print("Все записи уже обработаны или база пуста.")
            return

        for post in posts:
            text = (post.get("title", "") + " " + post.get("content", "")).lower()

            targets = list(
                {
                    value
                    for key, value in MAPPING["biological_targets"].items()
                    if key in text
                }
            )

            category = post.get("category")
            for key, value in MAPPING["categories"].items():
                if key in text:
                    category = value
                    break

            evidence = "review"
            for key, value in MAPPING["evidence"].items():
                if key in text:
                    evidence = value
                    break

            supabase.table("research_posts").update(
                {
                    "biological_targets": targets if targets else ["longevity"],
                    "category": category if category else "peptide",
                    "evidence_level": evidence,
                }
            ).eq("id", post["id"]).execute()

            print(
                f"Обновлена статья: {post.get('title','')} -> "
                f"{targets}, {category}, {evidence}"
            )


if __name__ == "__main__":
    analyze_and_update_optimized()
