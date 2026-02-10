import argparse
import json
import os
from datetime import datetime
from urllib import request
from urllib.error import HTTPError

import research_auto_ai as r


def _parse_post_id(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("POST_ID:"):
            return line.split(":", 1)[1].strip()
    return ""


def _list_recent_files(db_path: str, limit: int) -> list[str]:
    entries = [
        os.path.join(db_path, f)
        for f in os.listdir(db_path)
        if f.endswith(".txt") and os.path.isfile(os.path.join(db_path, f))
    ]
    entries.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return entries[:limit]


def _pretty_topic_from_path(path: str) -> str:
    name = os.path.splitext(os.path.basename(path))[0]
    if name.startswith("auto_"):
        name = name[len("auto_") :]
    return r._pretty_name(name)


def _update_lovable_image(post_id: str, image_url: str) -> dict:
    payload = {"post_id": post_id, "image_url": image_url}
    data = json.dumps(payload).encode("utf-8")

    def send(method: str) -> dict:
        req = request.Request(
            r.JOURNAL_ENDPOINT,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    try:
        return send("PATCH")
    except HTTPError as exc:
        if exc.code in (400, 404, 405):
            return send("POST")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill Lovable images")
    parser.add_argument("--limit", type=int, default=5, help="How many recent files to scan")
    args = parser.parse_args()

    db_path = os.path.join(os.getcwd(), "research_db")
    if not os.path.exists(db_path):
        print("research_db not found.")
        return 1

    files = _list_recent_files(db_path, args.limit)
    if not files:
        print("No research_db files found.")
        return 1

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        post_id = _parse_post_id(content)
        topic = _pretty_topic_from_path(path)
        if not post_id:
            print(f"Skipping {os.path.basename(path)}: POST_ID missing")
            continue
        prompt = r._build_image_prompt(topic)
        image_url = r._generate_image_url(prompt)
        if not image_url:
            print(f"Skipping {post_id}: image generation failed")
            continue
        response = _update_lovable_image(post_id, image_url)
        print(
            json.dumps(
                {
                    "post_id": post_id,
                    "topic": topic,
                    "image_url": image_url,
                    "response": response,
                    "updated_at": datetime.utcnow().isoformat(),
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
