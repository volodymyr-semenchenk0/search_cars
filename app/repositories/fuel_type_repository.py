from typing import Optional, List, Dict, Any

from app.db import execute_query
from app.utils.logger_config import logger


class FuelTypeRepository:
    @staticmethod
    def get_id_by_key_name(key_name: str) -> Optional[int]:
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

    @staticmethod
    def get_all_fuel_types() -> List[Dict[str, Any]]:

        sql = "SELECT key_name, label FROM fuel_types"
        try:
            return execute_query(sql)
        except Exception as e:
            logger.error(f"Помилка при отриманні всіх типів пального: {e}", exc_info=True)
            return []
