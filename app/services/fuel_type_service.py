from typing import List, Dict, Any

from app.repositories import FuelTypeRepository
from app.utils.logger_config import logger


class FuelTypeService:
    @staticmethod
    def list_all_fuel_types_for_select() -> List[Dict[str, Any]]:
        try:
            return FuelTypeRepository.get_all_fuel_types()
        except Exception as e:
            logger.error(f"FuelTypeService: Помилка при отриманні типів пального: {e}", exc_info=True)
            return []
