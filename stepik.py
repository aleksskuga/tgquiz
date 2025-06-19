# stepik.py
# Работа с API платформы Stepik 
import aiohttp
import base64

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

async def get_token_by_password(email, password, client_id, client_secret):
    url = f"{STEPIC_API_URL}/oauth2/token/"
    data = {
        "grant_type": "password",
        "username": email,
        "password": password,
    }
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            if resp.status != 200:
                return None, f"Ошибка авторизации: {resp.status}"
            return (await resp.json()).get("access_token"), None 

async def mark_step_completed(token: str, step_id: int):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{STEPIC_API_URL}/attempts"
    async with aiohttp.ClientSession(headers=headers) as session:
        # Создаём попытку
        data = {"step": step_id}
        async with session.post(url, json=data) as resp:
            if resp.status != 201:
                return False, f"Ошибка создания попытки: {resp.status}"
            attempt = (await resp.json())["attempts"][0]
            attempt_id = attempt["id"]
        # Отправляем пустой ответ (или любой валидный)
        url_sub = f"{STEPIC_API_URL}/submissions"
        data_sub = {"attempt": attempt_id, "reply": {}}
        async with session.post(url_sub, json=data_sub) as resp:
            if resp.status != 201:
                return False, f"Ошибка отправки ответа: {resp.status}"
        return True, None 