from typing import Optional

from app.db import execute_query
from app.utils.logger_config import logger


class CountryRepository:
    @staticmethod
    def get_id_by_code(country_code: str) -> Optional[int]:
        """
        Отримує ID країни за її ISO кодом (наприклад, 'DE').
        Повертає ID країни або None, якщо країну не знайдено.
        """
        if not country_code:
            logger.warning("Country code is not provided for ID lookup.")
            return None

        sql = "SELECT id FROM countries WHERE code = %s LIMIT 1"
        try:
            rows = execute_query(sql, (country_code,))
            if not rows:
                logger.warning(f"Країна з кодом '{country_code}' не знайдена в таблиці 'countries'.")
                return None
            return rows[0]['id']
        except Exception as e:
            logger.error(f"Помилка при отриманні ID країни за кодом '{country_code}': {e}", exc_info=True)
            return None
