# scheduler.py
# Периодический запуск задач-квизов
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from config import load_tokens, get_user_settings, DEBUG
from bot import quiz, tokens
import asyncio
import logging

scheduler = AsyncIOScheduler()

async def send_quiz_job(application):
    if DEBUG:
        print(f"[DEBUG] send_quiz_job вызван в {datetime.now()}")
    all_tokens = load_tokens()
    for user_id, data in all_tokens.items():
        settings = get_user_settings(user_id)
        period = settings.get('period_hours', 2)
        paused_until = settings.get('paused_until')
        if paused_until:
            try:
                if datetime.fromisoformat(paused_until) > datetime.now():
                    if DEBUG:
                        print(f"[DEBUG] {user_id}: пауза до {paused_until}")
                    continue
            except Exception as e:
                if DEBUG:
                    print(f"[DEBUG] Ошибка парсинга paused_until: {e}")
        # Проверка времени последней отправки (можно доработать для точного контроля)
        # Здесь просто отправляем квиз
        try:
            await application.bot.send_message(chat_id=user_id, text="Время для нового квиза! Используйте /quiz")
            if DEBUG:
                print(f"[DEBUG] Квиз отправлен {user_id}")
        except Exception as e:
            print(f"Ошибка отправки квиза {user_id}: {e}")


def start_scheduler(application):
    scheduler.add_job(send_quiz_job, 'interval', args=[application], hours=2)
    scheduler.start() 