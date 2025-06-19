# scheduler.py
# Периодический запуск задач-квизов
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from config import load_tokens, get_user_settings
from bot import quiz, tokens
import asyncio

scheduler = AsyncIOScheduler()

async def send_quiz_job(application):
    all_tokens = load_tokens()
    for user_id, data in all_tokens.items():
        settings = get_user_settings(user_id)
        period = settings.get('period_hours', 2)
        paused_until = settings.get('paused_until')
        if paused_until:
            try:
                if datetime.fromisoformat(paused_until) > datetime.now():
                    continue  # Пропустить, если пауза ещё действует
            except Exception:
                pass
        # Проверка времени последней отправки (можно доработать для точного контроля)
        # Здесь просто отправляем квиз
        try:
            await application.bot.send_message(chat_id=user_id, text="Время для нового квиза! Используйте /quiz")
        except Exception as e:
            print(f"Ошибка отправки квиза {user_id}: {e}")


def start_scheduler(application):
    scheduler.add_job(send_quiz_job, 'interval', args=[application], hours=2)
    scheduler.start() 