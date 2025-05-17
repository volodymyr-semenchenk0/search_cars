from typing import Optional

from app.db import execute_query
from app.utils.logger_config import logger


class FuelTypeRepository:
    @staticmethod
    def get_id_by_key_name(key_name: str) -> Optional[int]:
        """
        Отримує ID типу пального за його ключовою назвою (наприклад, 'diesel').
        Ваша таблиця 'fuel_types' має колонку 'key_name'.
        Повертає ID типу пального або None, якщо його не знайдено.
        """
        if not key_name:
            logger.warning("Fuel type key_name is not provided for ID lookup.")
            return None

        sql = "SELECT id FROM fuel_types WHERE key_name = %s LIMIT 1"
        try:
            rows = execute_query(sql, (key_name,))
            if not rows:
                logger.warning(f"Тип пального з key_name '{key_name}' не знайдений в таблиці 'fuel_types'.")
                return None
            return rows[0]['id']
        except Exception as e:
            logger.error(f"Помилка при отриманні ID типу пального за key_name '{key_name}': {e}", exc_info=True)
            return None
