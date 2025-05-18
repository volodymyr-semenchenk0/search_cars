from typing import Optional, List, Dict

from app.db import execute_query
from app.utils.logger_config import logger


class CountryRepository:
    @staticmethod
    def get_id_by_code(country_code: str) -> Optional[int]:

        if not country_code:
            logger.warning("Country code is not provided for ID lookup.")
            return None

        sql = "SELECT id FROM countries WHERE code = %s LIMIT 1"
        try:
            rows = execute_query(sql, (country_code,))
            if not rows:
                return None
            return rows[0]['id']
        except Exception as e:
            logger.error(f"Помилка при отриманні ID країни за кодом '{country_code}': {e}", exc_info=True)
            return None

    @staticmethod
    def get_all_countries_for_select() -> List[Dict[str, any]]:

        sql = "SELECT code, name, parsing_code FROM countries ORDER BY name ASC"
        try:
            return execute_query(sql)
        except Exception as e:
            logger.error(f"Помилка при отриманні всіх країн для вибору: {e}", exc_info=True)
            return []

    @staticmethod
    def get_parsing_code_by_iso_code(iso_code: str) -> Optional[str]:

        if not iso_code:
            logger.warning("ISO code is not provided for parsing_code lookup.")
            return None
        sql = "SELECT parsing_code FROM countries WHERE code = %s LIMIT 1"
        try:
            rows = execute_query(sql, (iso_code,))
            if rows and rows[0]['parsing_code']:
                return rows[0]['parsing_code']

            elif rows:
                logger.info(
                    f"Parsing_code for ISO code '{iso_code}' is NULL. Country exists but no specific parsing code.")
                return None
            else:
                logger.warning(f"No country found for ISO code '{iso_code}' during parsing_code lookup.")
                return None
        except Exception as e:
            logger.error(f"Помилка при отриманні parsing_code за ISO кодом '{iso_code}': {e}", exc_info=True)
            return None
