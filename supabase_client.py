from __future__ import annotations

import os
from pathlib import Path


def load_env(path: str | Path | None = None) -> dict[str, str]:
    if path is None:
        path = Path(__file__).resolve().parent / ".env"
    path = Path(path)
    if not path.exists():
        return {}

    env_vars: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        env_vars[key] = value
        os.environ.setdefault(key, value)
    return env_vars


def get_supabase_client():
    load_env()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

    try:
        from supabase import create_client
    except Exception as exc:  # pragma: no cover - best-effort for missing deps
        raise RuntimeError(
            "supabase-py not installed. Run: pip install supabase"
        ) from exc

    return create_client(url, key)
