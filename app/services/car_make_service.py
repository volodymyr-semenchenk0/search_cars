from typing import Optional

from app.repositories import CarMakeRepository
from app.utils.logger_config import logger


class CarMakeService:
    @staticmethod
    def get_all_makes_for_select() -> list[dict]:
        try:
            return CarMakeRepository.get_all_makes_for_select()
        except Exception as e:
            logger.error(f"Помилка в CarMakeService при отриманні марок: {e}")
            return []

    @staticmethod
    def get_make_name_by_id(make_id: int) -> Optional[str]:

        if not isinstance(make_id, int) or make_id <= 0:
            logger.warning(f"CarMakeService: Отримано невалідний make_id ({make_id}) для пошуку назви.")
            return None
        try:
            name = CarMakeRepository.get_name_by_id(make_id)
            if not name:
                return None
            return name
        except Exception as e:
            logger.error(f"CarMakeService: Помилка при отриманні назви марки за ID {make_id}: {e}", exc_info=True)
            return None
