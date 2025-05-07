# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from typing import Optional

load_dotenv()

def get_llm() -> ChatOpenAI:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY не найден в .env.")

    return ChatOpenAI(
        model_name="gpt-3.5-turbo-0125",
        temperature=0,
        max_tokens=256,  # уменьшено
        request_timeout=10,  # ограничим ожидание
        openai_api_key=api_key
    )

def get_admin_password() -> Optional[str]:
    """Возвращает пароль администратора."""
    return os.getenv("ADMIN_PASSWORD")

def get_db_uri() -> str:
    """Возвращает URI подключения к SQLite базе данных."""
    return os.getenv("DB_URI", "sqlite:///db/products.db")