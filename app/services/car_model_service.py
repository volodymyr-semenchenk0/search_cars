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
