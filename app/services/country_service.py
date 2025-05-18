from typing import List, Dict, Any
from app.repositories import CountryRepository
from app.utils.logger_config import logger

class CountryService:
    @staticmethod
    def get_countries_for_select() -> List[Dict[str, Any]]:

        try:
            countries_from_db = CountryRepository.get_all_countries_for_select()
            return countries_from_db
        except Exception as e:
            logger.error(f"CountryService: Помилка при отриманні країн для вибору: {e}", exc_info=True)
            return []