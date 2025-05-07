# -*- coding: utf-8 -*-
import re
import ast
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_core.messages import SystemMessage
from langchain_community.utilities import SQLDatabase

from agent.config import get_llm, get_db_uri
from agent.db_utils import log_query


class AgentWithLogging:
    """
    Минимальный агент LangChain с извлечением SQL-запроса из ответа модели.
    """

    def __init__(self):
        self.llm = get_llm()
        self.db = SQLDatabase.from_uri(
            get_db_uri(),
            include_tables=["products"],
            sample_rows_in_table_info=0
        )

        self.tool = Tool(
            name="query_products",
            func=self.db.run,
            description="Выполняет SQL-запросы к таблице 'products' с полями name, price, category, description"
        )

        system_message = SystemMessage(
            content=(
                "Ты SQL-ассистент. Отвечай ТОЛЬКО корректными SQL-запросами к таблице 'products'. "
                "Не используй JSON, не пиши комментарии. Просто верни запрос вида: "
                "SELECT * FROM products WHERE ..."
            )
        )

        self.agent = initialize_agent(
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            tools=[self.tool],
            llm=self.llm,
            agent_kwargs={"system_message": system_message},
            memory=None,
            verbose=False
        )

    def run(self, user_query: str) -> str:
        try:
            result = self.agent.invoke(user_query)['output']  # Часто результат агента в словаре под ключом 'output'

            if isinstance(result, str):
                match = re.search(r"command='([^']*)'", result)  # Ищем паттерн command='SQL_QUERY'
                if match:
                    result = match.group(1)  # Если нашли, извлекаем сам SQL_QUERY
                result = result.strip().strip("'").strip('"')

            if not result:
                raise ValueError("Агент вернул пустой результат после обработки.")

            print(f"DEBUG: Выполняется SQL: {result}")  # Добавим отладочный вывод

            log_query(user_query, result, "Executing...")  # Логгируем фактический SQL

            db_result = self.db.run(result)
            log_query(user_query, result, str(db_result))  # Логгируем результат выполнения
            return str(db_result)  # Возвращаем результат выполнения как строку

        except Exception as e:
            # Логгируем ошибку перед тем как пробросить её дальше
            error_message = f"Ошибка при выполнении запроса: {e}"
            try:
                log_query(user_query, result if 'result' in locals() else "[SQL не извлечен]", error_message)
            except Exception as log_e:
                print(f"DEBUG: Не удалось залогировать ошибку: {log_e}")  # Отладка для логирования

            raise RuntimeError(error_message)
def create_agent() -> AgentWithLogging:
    return AgentWithLogging()