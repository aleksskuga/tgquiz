# Telegram Quiz Bot for Stepik

Этот проект — Telegram-бот для регулярного квизинга пользователей Stepik. Бот интегрируется с Stepik API и OpenAI API, чтобы каждые 2 часа отправлять пользователю квиз по текущему уроку. MVP хранит токены пользователей в JSON-файле, использует APScheduler для планирования задач и деплоится через Railway.

## Основные возможности
- Авторизация через Stepik-токен
- Получение текущего урока пользователя
- Генерация квиза с помощью OpenAI
- Отправка квиза с кнопками в Telegram
- Обработка ответов пользователя
- Планировщик отправки квизов каждые 2 часа

## Стек технологий
- Python 3.11+
- python-telegram-bot
- openai
- aiohttp
- python-dotenv
- APScheduler

## Запуск
1. Склонируйте репозиторий
2. Установите зависимости из requirements.txt
3. Заполните .env (TELEGRAM_TOKEN, OPENAI_API_KEY)
4. Запустите bot.py

Подробности — в документации и implementation_plan.mdc  .txt 

## Структура проекта

- bot.py — точка входа Telegram-бота
- config.py — конфигурация и переменные окружения
- stepik.py — работа с API Stepik
- quiz_generator.py — генерация квизов через OpenAI
- scheduler.py — планировщик задач
- .env — секреты и ключи окружения
- requirements.txt — зависимости
- Procfile — запуск Railway
- tokens.json — хранилище токенов пользователей 