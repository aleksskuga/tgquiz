# config.py
# Конфигурация и переменные окружения
import os
import json

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOKENS_FILE = "tokens.json"
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def get_user_settings(user_id):
    tokens = load_tokens()
    return tokens.get(user_id, {})

def set_user_settings(user_id, **kwargs):
    tokens = load_tokens()
    user = tokens.get(user_id, {})
    user.update(kwargs)
    tokens[user_id] = user
    save_tokens(tokens) 