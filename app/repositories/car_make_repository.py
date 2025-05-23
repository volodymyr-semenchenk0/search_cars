from typing import Optional, List, Dict

from app.db import execute_query, get_db_connection
from app.utils.logger_config import logger


class CarMakeRepository:
    @staticmethod
    def get_id_by_name(make_name: str) -> Optional[int]:
        if not make_name:
            logger.warning("Make name is not provided for ID lookup.")
            return None

        make_name_clean = make_name.strip()
        if not make_name_clean:
            logger.warning("Cleaned make name is empty.")
            return None

        sql = "SELECT id FROM car_makes WHERE name = %s LIMIT 1"
        try:
            rows = execute_query(sql, (make_name_clean,))
            return rows[0]['id'] if rows else None
        except Exception as e:
            logger.error(f"Помилка при отриманні ID марки за назвою '{make_name_clean}': {e}", exc_info=True)
            return None

    @staticmethod
    def create(make_name: str) -> Optional[int]:
        make_name_clean = make_name.strip()
        logger.info(f"Спроба створити нову марку: '{make_name_clean}'")

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql_insert = "INSERT INTO car_makes (name, country_id) VALUES (%s, NULL)"
            cursor.execute(sql_insert, (make_name_clean,))
            make_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Створено нову марку '{make_name_clean}' з ID {make_id}.")
            return make_id
        except Exception as e:
            if conn and conn.is_connected():
                conn.rollback()
            logger.error(f"Помилка створення марки '{make_name_clean}': {e}", exc_info=True)
            return None
        finally:
            if conn and conn.is_connected():
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()

    @staticmethod
    def get_or_create_id(make_name: str) -> Optional[int]:
        if not make_name:
            logger.warning("Make name is not provided for get_or_create_id.")
            return None

        make_name_clean = make_name.strip()
        if not make_name_clean:
            logger.warning("Cleaned make name is empty for get_or_create_id.")
            return None

        make_id = CarMakeRepository.get_id_by_name(make_name_clean)
        if make_id:
            return make_id

        return CarMakeRepository.create(make_name_clean)

    @staticmethod
    def get_all_makes_for_select() -> List[Dict[str, any]]:
        sql = "SELECT id, name FROM car_makes ORDER BY name ASC"
        try:
            return execute_query(sql)
        except Exception as e:
            logger.error(f"Помилка отримання всіх марок для вибору: {e}", exc_info=True)
            return []


    @staticmethod
    def get_name_by_id(make_id: int) -> Optional[str]:

        if not isinstance(make_id, int) or make_id <= 0:
            logger.warning(f"Некоректний Make ID ({make_id}) надано для пошуку назви.")
            return None
        sql = "SELECT name FROM car_makes WHERE id = %s LIMIT 1"
        try:
            rows = execute_query(sql, (make_id,))
            return rows[0]['name'] if rows else None
        except Exception as e:
            logger.error(f"Помилка при отриманні назви марки за ID '{make_id}': {e}", exc_info=True)
            return None