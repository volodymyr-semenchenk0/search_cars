from typing import Optional, List, Dict

from app.db import execute_query, get_db_connection
from app.utils.logger_config import logger


class CarModelRepository:
    @staticmethod
    def get_id_by_make_id_and_name(make_id: int, model_name: str) -> Optional[int]:
        if not model_name:
            logger.warning("Model name is not provided for ID lookup.")
            return None
        if not make_id:
            logger.warning("Make ID is not provided for model lookup.")
            return None

        model_name_clean = model_name.strip()
        if not model_name_clean:
            logger.warning("Cleaned model name is empty.")
            return None

        sql = "SELECT id FROM car_models WHERE make_id = %s AND name = %s LIMIT 1"
        try:
            rows = execute_query(sql, (make_id, model_name_clean))
            return rows[0]['id'] if rows else None
        except Exception as e:
            logger.error(f"Помилка при отриманні ID моделі '{model_name_clean}' для make_id {make_id}: {e}",
                         exc_info=True)
            return None

    @staticmethod
    def create(make_id: int, model_name: str) -> Optional[int]:
        model_name_clean = model_name.strip()
        logger.info(f"Спроба створити нову модель: '{model_name_clean}' для make_id: {make_id}")

        if not make_id:
            logger.error(f"Не можливо створити модель '{model_name_clean}' без make_id.")
            return None

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql_insert = "INSERT INTO car_models (make_id, name) VALUES (%s, %s)"
            cursor.execute(sql_insert, (make_id, model_name_clean))
            model_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Створено нову модель '{model_name_clean}' з ID {model_id} для make_id {make_id}.")
            return model_id
        except Exception as e:
            if conn and conn.is_connected():
                conn.rollback()
            logger.error(f"Помилка створення моделі '{model_name_clean}' для make_id {make_id}: {e}", exc_info=True)
            return None
        finally:
            if conn and conn.is_connected():
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()

    @staticmethod
    def get_or_create_id(make_id: int, model_name: str) -> Optional[int]:
        if not model_name:
            logger.warning("Model name is not provided for get_or_create_id.")
            return None
        if not make_id:
            logger.error("Make ID is required for get_or_create_id of a model.")
            return None

        model_name_clean = model_name.strip()
        if not model_name_clean:
            logger.warning("Cleaned model name is empty for get_or_create_id.")
            return None

        model_id = CarModelRepository.get_id_by_make_id_and_name(make_id, model_name_clean)
        if model_id:
            return model_id

        return CarModelRepository.create(make_id, model_name_clean)

    @staticmethod
    def get_models_by_make_id_for_select(make_id: int) -> List[Dict[str, any]]: # Змінив list[dict] на List[Dict[str, any]]
        if not make_id:
            return []
        sql = "SELECT id, name FROM car_models WHERE make_id = %s ORDER BY name ASC"
        try:
            return execute_query(sql, (make_id,))
        except Exception as e:
            logger.error(f"Помилка отримання моделей для make_id {make_id}: {e}", exc_info=True)
            return []

    # --- НОВИЙ МЕТОД ---
    @staticmethod
    def get_name_by_id(model_id: int) -> Optional[str]:
        """
        Отримує назву моделі за її ID.
        """
        if not isinstance(model_id, int) or model_id <= 0: # Додав перевірку типу та значення
            logger.warning(f"Некоректний Model ID ({model_id}) надано для пошуку назви.")
            return None
        sql = "SELECT name FROM car_models WHERE id = %s LIMIT 1"
        try:
            rows = execute_query(sql, (model_id,))
            return rows[0]['name'] if rows else None
        except Exception as e:
            logger.error(f"Помилка при отриманні назви моделі за ID '{model_id}': {e}", exc_info=True)
            return None
    # --- КІНЕЦЬ НОВОГО МЕТОДУ ---

