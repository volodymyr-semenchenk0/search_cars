from typing import Optional

from app.repositories import CarModelRepository
from app.utils.logger_config import logger


class CarModelService:
    @staticmethod
    def get_models_for_make_for_select(make_id: int) -> list[dict]:

        if not isinstance(make_id, int) or make_id <= 0:
            logger.warning(f"CarModelService: Отримано невалідний make_id: {make_id}")
            return []
        try:
            return CarModelRepository.get_models_by_make_id_for_select(make_id)
        except Exception as e:
            logger.error(f"CarModelService: Помилка при отриманні моделей для make_id {make_id}: {e}", exc_info=True)
            return []

    @staticmethod
    def get_model_name_by_id(model_id: int) -> Optional[str]:
        if not isinstance(model_id, int) or model_id <= 0:
            logger.warning(f"CarModelService: Отримано невалідний model_id ({model_id}) для пошуку назви.")
            return None
        try:
            name = CarModelRepository.get_name_by_id(model_id)
            if not name:
                logger.warning(f"CarModelService: Модель з ID {model_id} не знайдена.")
                return None
            return name
        except Exception as e:
            logger.error(f"CarModelService: Помилка при отриманні назви моделі за ID {model_id}: {e}", exc_info=True)
            return None
