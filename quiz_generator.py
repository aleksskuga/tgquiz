# quiz_generator.py
# Генерация квизов через OpenAI GPT
import openai
from config import OPENAI_API_KEY
import re

async def generate_quiz(title: str, topic: str, text: str) -> str:
    prompt = (
        f"Сгенерируй один вопрос квиза по теме '{topic}' из урока '{title}'. "
        f"Текст урока: {text}\n"
        "Ответ должен быть в формате: Вопрос + 4 варианта ответа (A, B, C, D), где только один правильный. "
        "Укажи правильный вариант явно."
    )
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4-1106-preview",  # gpt-4.1-mini
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def parse_quiz(quiz_text: str):
    # Пример ожидаемого формата:
    # Вопрос: ...\nA) ...\nB) ...\nC) ...\nD) ...\nПравильный ответ: B
    lines = quiz_text.strip().splitlines()
    question = lines[0]
    options = []
    correct = None
    for line in lines[1:]:
        m = re.match(r"([A-D])\)?[\.:\)]?\s*(.*)", line)
        if m:
            options.append((m.group(1), m.group(2)))
        if "правильный ответ" in line.lower():
            correct = line.split(":")[-1].strip().upper()
    return question, options, correct 