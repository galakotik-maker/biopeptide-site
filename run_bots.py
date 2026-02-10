import os
import subprocess
import sys

from dotenv import load_dotenv

# Environment setup
load_dotenv()

os.environ["ARBITER_TOKEN"] = "8337375430:AAH_EF7VRsS3H3zndUEV3YArbjoaISIq1Xk"
os.environ["DR_DRAG_TOKEN"] = "7951815604:AAEjDfOA50M7RHGmueJY7SXbs5jhBT3UJis"
os.environ["TELEGRAM_BOT_TOKEN"] = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ[
    "DR_DRAG_TOKEN"
]
os.environ["SUPABASE_KEY"] = "sb_publishable_JAPstHq5F-5szM6U-bOJfg_mpo-hyfJ"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "sb_secret__03xPN3mtKaV1OCw1d5mbg_eojACOhl"
os.environ["TELEGRAM_CHANNEL_ID"] = "@BioPeptideResearch"
os.environ["NEWS_ARTICLES_TEXT_EN_FIELD"] = "content"
os.environ["NEWS_ARTICLES_TEXT_RU_FIELD"] = "title"


def main() -> int:
    print("Starting bots in separate processes.")
    processes = []
    for script in ("comment_handler.py", "dr_drag_bot.py"):
        if not os.path.exists(script):
            print(f"Missing {script}")
            continue
        processes.append(subprocess.Popen([sys.executable, script]))

    if not processes:
        return 1

    for process in processes:
        process.wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
