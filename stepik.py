# stepik.py
# Работа с API платформы Stepik 
import aiohttp

STEPIC_API_URL = "https://stepik.org/api"

async def get_current_lesson(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        # Получаем профиль пользователя
        async with session.get(f"{STEPIC_API_URL}/users/me") as resp:
            if resp.status != 200:
                return None, "Ошибка авторизации Stepik"
            user = (await resp.json())["users"][0]
            last_step = user.get("last_step")
            if not last_step:
                return None, "Не найден last_step в профиле"
        # Получаем step
        async with session.get(f"{STEPIC_API_URL}/steps/{last_step}") as resp:
            if resp.status != 200:
                return None, "Ошибка получения step"
            step = (await resp.json())["steps"][0]
            lesson_id = step["lesson"]
        # Получаем lesson
        async with session.get(f"{STEPIC_API_URL}/lessons/{lesson_id}") as resp:
            if resp.status != 200:
                return None, "Ошибка получения lesson"
            lesson = (await resp.json())["lessons"][0]
        # Возвращаем данные урока
        return {
            "title": lesson.get("title", ""),
            "topic": step.get("block", {}).get("name", ""),
            "text": step.get("block", {}).get("text", ""),
        }, None 