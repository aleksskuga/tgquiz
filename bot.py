# bot.py
# Основной запуск Telegram-бота
import logging
import os
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from config import TELEGRAM_TOKEN, load_tokens, save_tokens, get_user_settings, set_user_settings
from dotenv import load_dotenv
from stepik import get_current_lesson, get_token_by_password, mark_step_completed
from quiz_generator import generate_quiz, parse_quiz
import asyncio
from scheduler import start_scheduler

load_dotenv()

logging.basicConfig(level=logging.INFO)

ASK_TOKEN = 1

tokens = load_tokens()

PERIOD_OPTIONS = [
    ("2 часа", 2),
    ("4 часа", 4),
    ("1 раз в день", 24),
]

def get_user_id(update: Update) -> str:
    return str(update.effective_user.id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Отправь мне свой Stepik токен для интеграции.\n\n" 
        "Его можно получить в настройках Stepik: https://stepik.org/edit-profile"
    )
    return ASK_TOKEN

async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = get_user_id(update)
    token = update.message.text.strip()
    tokens[user_id] = token
    save_tokens(tokens)
    await update.message.reply_text("Токен сохранён! Теперь бот сможет отправлять тебе квизы.")
    return ConversationHandler.END

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update)
    token = tokens.get(user_id)
    if not token:
        await update.message.reply_text("Сначала отправьте Stepik токен через /start.")
        return
    await update.message.reply_text("Получаю ваш урок на Stepik...")
    lesson, err = await get_current_lesson(token)
    if err:
        await update.message.reply_text(f"Ошибка Stepik: {err}")
        return
    await update.message.reply_text("Генерирую квиз через OpenAI...")
    quiz_text = await generate_quiz(lesson['title'], lesson['topic'], lesson['text'])
    question, options, correct = parse_quiz(quiz_text)
    context.user_data['correct'] = correct
    context.user_data['step_id'] = lesson.get('step_id') or lesson.get('id')
    keyboard = [[InlineKeyboardButton(f"{opt[0]}) {opt[1]}", callback_data=opt[0])] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_answer = query.data
    correct = context.user_data.get('correct')
    user_id = get_user_id(update)
    token = tokens.get(user_id)
    step_id = context.user_data.get('step_id')
    if user_answer == correct:
        # Отметить шаг завершённым
        if token and step_id:
            ok, err = await mark_step_completed(token, step_id)
            if ok:
                await query.edit_message_text("✅ Верно! Переходим к следующему уроку.")
            else:
                await query.edit_message_text(f"✅ Верно! Но не удалось отметить урок завершённым: {err}")
        else:
            await query.edit_message_text("✅ Верно! (step_id не найден)")
    else:
        await query.edit_message_text(f"❌ Неверно. Правильный ответ: {correct}\nЭтот урок будет повторён.")

async def period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"period_{hours}")]
        for label, hours in PERIOD_OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите периодичность отправки квизов:", reply_markup=reply_markup)

async def period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    if query.data.startswith("period_"):
        hours = int(query.data.split("_")[1])
        set_user_settings(user_id, period_hours=hours, paused_until=None)
        await query.edit_message_text(f"Периодичность квизов установлена: раз в {hours} ч.")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime, timedelta
    user_id = get_user_id(update)
    tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    set_user_settings(user_id, paused_until=tomorrow.isoformat())
    await update.message.reply_text("Автоотправка квизов отключена до следующего дня.")

async def get_stepik_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Использовать только для теста! Не хранить реальные данные в продакшене.
    if len(context.args) != 4:
        await update.message.reply_text("Использование: /get_stepik_token email password client_id client_secret")
        return
    email, password, client_id, client_secret = context.args
    await update.message.reply_text("Пробую получить токен Stepik...")
    token, err = await get_token_by_password(email, password, client_id, client_secret)
    if err:
        await update.message.reply_text(f"Ошибка: {err}")
    else:
        await update.message.reply_text(f"Ваш access_token: {token}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_token)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("period", period))
    application.add_handler(CommandHandler("pause", pause))
    application.add_handler(CommandHandler("get_stepik_token", get_stepik_token))
    application.add_handler(MessageHandler(filters.StatusUpdate.CALLBACK_QUERY, answer_callback))
    application.add_handler(MessageHandler(filters.StatusUpdate.CALLBACK_QUERY, period_callback))

    start_scheduler(application)

    application.run_polling()

if __name__ == "__main__":
    main() 