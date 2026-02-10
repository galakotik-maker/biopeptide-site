import os
from dotenv import load_dotenv
from supabase import create_client, Client


KEEP_POST_ID = "aea701ac-1eab-4ed5-84ba-3bfbb254fa84"


def main() -> None:
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_ANON_KEY")

    supabase: Client = create_client(supabase_url, supabase_key)
    response = supabase.table("journal_posts").delete().neq("id", KEEP_POST_ID).execute()
    deleted = response.data or []
    print(f"Deleted journal_posts rows: {len(deleted)} (kept {KEEP_POST_ID})")


if __name__ == "__main__":
    main()
