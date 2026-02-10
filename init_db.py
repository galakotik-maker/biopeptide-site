from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from supabase_client import load_env


CREATE_TABLE_SQL = """
create table if not exists public.news_articles (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text,
  url text,
  created_at timestamptz not null default now()
);
""".strip()


def _is_publishable_key(key: str) -> bool:
    lowered = key.lower()
    return lowered.startswith("sb_publishable") or lowered.startswith("anon")


def create_table_via_pg_meta(url: str, key: str) -> None:
    endpoints = [
        ("/pg-meta/query", {"query": CREATE_TABLE_SQL}),
        ("/pg-meta/sql", {"query": CREATE_TABLE_SQL}),
        ("/pg-meta/query", {"sql": CREATE_TABLE_SQL}),
        ("/pg-meta/sql", {"sql": CREATE_TABLE_SQL}),
    ]

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
                body = response.read().decode("utf-8").strip()
                print("Table creation request sent successfully.")
                if body:
                    print(body)
                return
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8").strip()
            last_error = (exc.code, body)
            if exc.code not in {404, 401, 403}:
                print(f"Failed to create table (HTTP {exc.code}).")
                if body:
                    print(body)
                raise SystemExit(1) from exc

    if last_error:
        code, body = last_error
        print(f"Failed to create table (HTTP {code}).")
        if body:
            print(body)
    raise SystemExit(1)


def main() -> None:
    load_env()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        print(
            "Missing SUPABASE_URL or SUPABASE_KEY in .env. "
            "For DDL, SUPABASE_SERVICE_ROLE_KEY is recommended."
        )
        sys.exit(1)

    if _is_publishable_key(key):
        print(
            "Warning: publishable/anon key detected. "
            "Table creation may be blocked without a service role key."
        )

    create_table_via_pg_meta(url, key)


if __name__ == "__main__":
    main()
