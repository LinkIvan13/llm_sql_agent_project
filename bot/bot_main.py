# -*- coding: utf-8 -*-
import sys
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Добавляем корень проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent import create_agent
from agent.db_utils import init_telegram_logs, log_telegram_query

# Загрузка .env-переменных
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создание агента один раз
agent = create_agent()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я SQL-бот. Напиши мне запрос на русском, и я найду данные в базе 📦."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(2)  # 🔄 защита от спама: задержка перед выполнением

    user = update.effective_user
    user_input = update.message.text

    try:
        response = agent.run(user_input)

        # Логируем запрос в БД
        log_telegram_query(
            user_id=user.id,
            username=user.username or "unknown",
            query=user_input,
            result=str(response)
        )

        await update.message.reply_text(f"🧠 Ответ:\n{response}")

    except Exception as e:
        if "rate_limit_exceeded" in str(e).lower():
            await update.message.reply_text(
                "⚠️ Превышен лимит токенов OpenAI. Пожалуйста, подождите и попробуйте позже."
            )
        else:
            await update.message.reply_text(f"⚠️ Ошибка: {e}")


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN не найден в .env")

    # Создание таблицы логов при старте
    init_telegram_logs()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Telegram-бот запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
