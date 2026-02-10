import json
from urllib import request


JOURNAL_ENDPOINT = "https://fmtbdjyaqgszzzzcrhdk.supabase.co/functions/v1/journal-bot"


def send_journal_post(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        JOURNAL_ENDPOINT,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    payload = {
        "title": "Mason Jar Fermentation: Технология будущего",
        "content": (
            "Подробный разбор того, как использование Mason Jar Kits помогает "
            "оптимизировать микробиом кишечника через контролируемую ферментацию. "
            "Научный подход к домашним пробиотикам."
        ),
        "category": "science",
        "is_published": True,
    }
    response = send_journal_post(payload)
    print("Response:", response)


if __name__ == "__main__":
    main()
