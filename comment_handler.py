from __future__ import annotations

import asyncio
import json
import os
import re
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()

# Абсолютный путь к базе знаний
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "research_db")

URL_REGEX = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)
MENTION_REGEX = re.compile(r"@\w+", re.IGNORECASE)

BANNED_PHRASES = [
    "купить здесь",
    "в личку",
    "переходите",
    "лучшая цена",
    "идиот",
    "дурак",
    "тупой",
    "мразь",
    "ублюдок",
    "ненавижу",
]

WARNING_TEXT = (
    "❌ Нарушение правил BioPeptidePlus. Реклама, спам и попытки переманивания "
    "пользователей запрещены. Повторное нарушение — бан"
)


def _scan_db_files(db_dir: str) -> dict[str, str]:
    """
    Возвращает словарь: базовый_нейм_файла (lowercase) -> полное_имя_файла
    """
    if not os.path.isdir(db_dir):
        return {}
    files = [
        f
        for f in os.listdir(db_dir)
        if f.lower().endswith(".txt") and os.path.isfile(os.path.join(db_dir, f))
    ]
    # Ключ — нормализованное имя файла (без .txt), значение — имя файла
    return {_normalize_token(os.path.splitext(f)[0]): f for f in files}


def _normalize_token(text: str) -> str:
    lowered = text.lower()
    return re.sub(r"[-\s]+", "", lowered)


def _normalize_keyword(word: str) -> str:
    lowered = word.lower()
    ru_map = {
        "тирзепатид": "tirzepatide",
        "семакс": "semax",
        "селанк": "selank",
        "бпк157": "bpc157",
        "тб500": "tb500",
    }
    mapped = ru_map.get(lowered, lowered)
    return _normalize_token(mapped)


def _is_violation(text: str) -> bool:
    lowered = text.lower()
    if URL_REGEX.search(text):
        return True
    if MENTION_REGEX.search(text):
        return True
    return any(phrase in lowered for phrase in BANNED_PHRASES)


async def _delete_warning_later(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_id: int
) -> None:
    await asyncio.sleep(10)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass


async def _delete_notice_later(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_id: int
) -> None:
    await asyncio.sleep(5)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass


async def _is_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
    except Exception:
        return False
    return any(admin.user.id == user_id for admin in admins)

def get_peptide_info(query: str, db_dir: str = DB_PATH) -> str:
    """
    Ищет файл {название}.txt по запросу пользователя.
    Нормализует дефисы и пробелы, поддерживает русский ввод.
    """
    print(f"[ЛОГ] Получено сообщение: {query!r}")

    if not os.path.isdir(db_dir):
        print(f"[ЛОГ] research_db не найдена: {db_dir}")
        return "⚖️ В моей базе пока нет данных по этим ключевым словам, но я могу поискать их в сети. Найти?"

    files_map = _scan_db_files(db_dir)
    current_files = sorted(files_map.values())

    raw_lower = query.lower().strip()
    stop_words = {"протокол", "инфо", "справка"}
    for word in stop_words:
        raw_lower = raw_lower.replace(word, " ")
    raw_lower = " ".join(raw_lower.split())
    MAPPING = {
        "тирзепатид": "tirzepatide",
        "семакс": "semax",
        "селанк": "selank",
        "эпиталон": "epitalon",
        "бпк157": "bpc157",
        "тб500": "tb500",
    }

    if raw_lower in MAPPING:
        normalized = MAPPING[raw_lower]
    else:
        normalized = " ".join(query.lower().split())
    normalized = _normalize_token(normalized)
    if "motsc" in normalized:
        normalized = "mots-c"

    words = re.findall(r"\w+", normalized)
    name = _normalize_keyword(words[0]) if words else _normalize_keyword(normalized)
    normalized_name = _normalize_token(name)

    resolved = files_map.get(normalized_name)
    file_name = resolved or f"{normalized_name}.txt"
    file_path = os.path.join(db_dir, file_name)

    print(f"DEBUG: Ищу файл {file_name} по пути {file_path}")
    print(f"АРБИТР ИЩЕТ ТУТ: {file_path}")

    if not os.path.isfile(file_path):
        print(f"DEBUG: Не нашел {file_name} в {db_dir}")
        print(f"DEBUG: В папке сейчас лежат файлы: {current_files}")
        return "В базе BioPeptidePlus пока нет данных по этому запросу"

    print("DEBUG: Файл найден, отправляю данные")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_contents = f.read()

        cleaned = _clean_text(file_contents)
        peptide_name = os.path.splitext(file_name)[0]
        if not cleaned.strip():
            return "Файл найден, но данных внутри пока нет"

        return f"🔬 **Экспертный анализ BioPeptidePlus: {peptide_name}**\n\n{cleaned.strip()}"
    except Exception as e:
        print(f"[ОШИБКА] Ошибка при чтении файла: {e}")
        return f"⚖️ Произошла ошибка при чтении файла базы знаний. ({e})"


def _clean_text(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("---"):
            continue
        if line.startswith("AUTO ENTRY"):
            continue
        if "AUTO ENTRY" in line or "DATA ENTRY" in line:
            continue
        if re.search(r"\b\d{4}[-/.]\d{2}[-/.]\d{2}\b", line):
            continue
        if re.search(r"\b\d{8,}\b", line):
            continue
        if line.startswith("⚖️"):
            continue
        lines.append(line)
    return "\n".join(lines)




async def _handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает сообщение Telegram и отправляет ответ.
    """
    try:
        if not update.message or not update.message.text:
            return
        chat_id = update.message.chat_id
        text = update.message.text
        print(f"[ЛОГ] Новый запрос из чата {chat_id}, текст: {text!r}")

        # 1) Модерация/спам/ссылки/упоминания
        if _is_violation(text):
            try:
                await context.bot.delete_message(
                    chat_id=chat_id, message_id=update.message.message_id
                )
            except Exception:
                return
            warning = await update.message.reply_text(WARNING_TEXT)
            asyncio.create_task(
                _delete_warning_later(context, chat_id, warning.message_id)
            )
            return

        # 2) Команда /clear (только администратор)
        if text.strip().lower().startswith("/clear"):
            user_id = update.message.from_user.id if update.message.from_user else None
            if user_id is None or not await _is_admin(context, chat_id, user_id):
                return
            try:
                await context.bot.delete_message(
                    chat_id=chat_id, message_id=update.message.message_id
                )
            except Exception:
                pass
            # Удаляем последние 100 сообщений, начиная с текущего
            current_id = update.message.message_id
            for msg_id in range(current_id, max(current_id - 100, 0), -1):
                try:
                    print(f"DEBUG: Удаляю сообщение ID={msg_id}")
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except Exception:
                    continue
                await asyncio.sleep(0.1)
            notice = await context.bot.send_message(
                chat_id=chat_id,
                text="🧹 Чат очищен (насколько позволили лимиты Telegram)",
            )
            asyncio.create_task(_delete_notice_later(context, chat_id, notice.message_id))
            return

        # 3) Поиск по базе
        reply_text = get_peptide_info(text)
        await update.message.reply_text(reply_text, parse_mode="Markdown")
    except Exception as e:
        print(f"[ОШИБКА] При обработке сообщения: {e}")
    finally:
        print("DEBUG: Бот готов к следующему запросу")

def run_polling() -> None:
    token = os.getenv("ARBITER_TOKEN")
    if not token:
        print("Missing ARBITER_TOKEN in .env")
        sys.exit(1)

    print(f"Путь к базе: {DB_PATH}")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT, _handle_update))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run_polling()




