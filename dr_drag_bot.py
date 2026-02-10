import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Загрузка настроек
load_dotenv()
TOKEN = os.getenv("DR_DRAG_TOKEN")

# Настройка логирования, чтобы видеть ошибки в терминале
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def drag_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        text = update.message.text
        user = update.message.from_user.username
        chat_id = update.message.chat_id
        print(f"От: @{user} | В чате: {chat_id} | Текст: {text}")

        # Реакция только на запросы по дозировкам/расчетам
        lower_text = text.lower()
        keywords = ["дозировка", "расчет", "сколько", "мкг", "мг"]
        if not any(word in lower_text for word in keywords):
            return

        response = (
            "💊 Dr. Drag: Стандартный протокол — 5 мкг на 1 кг веса. "
            "Для примера: Если твой вес 80 кг, доза составит 400 мкг. "
            "За подробным описанием свойств иди к Арбитру."
        )

        try:
            await update.message.reply_text(response)
            print("[v] Ответ отправлен успешно!")
        except Exception as e:
            print(f"[x] ОШИБКА ОТПРАВКИ: {e}")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Ключ DR_DRAG_TOKEN не найден!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        # Слушаем ВСЕ текстовые сообщения в группах и личке
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), drag_logic))
        
        print("✅ Двигатель запущен. Жду сообщений в Telegram...")
        app.run_polling(drop_pending_updates=True)
        