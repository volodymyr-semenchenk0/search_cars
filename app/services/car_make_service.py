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