import os
import subprocess


QUEUE_PATH = os.path.join(os.getcwd(), "topics_queue.txt")


def load_topics(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_topics(path: str, topics: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(topics) + ("\n" if topics else ""))


def publish_topic(topic: str) -> int:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    result = subprocess.run(
        ["python3", "research_auto_ai.py", "--topic", topic],
        cwd=os.getcwd(),
        env=env,
        check=False,
    )
    return result.returncode


def main() -> int:
    topics = load_topics(QUEUE_PATH)
    if not topics:
        print("No topics left in topics_queue.txt")
        return 0

    batch = topics[:2]
    remaining = topics[2:]
    save_topics(QUEUE_PATH, remaining)

    exit_code = 0
    for topic in batch:
        print(f"Publishing topic: {topic}")
        code = publish_topic(topic)
        if code != 0:
            print(f"Failed topic: {topic} (exit {code})")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
