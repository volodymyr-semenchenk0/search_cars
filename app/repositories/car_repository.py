# app/repositories/car_repository.py
from typing import Optional, Dict, Any

from app.utils.logger_config import logger


class CarRepository:
    @staticmethod
    def create_car_with_powertrain(data: Dict[str, Any], cursor: Any) -> Optional[int]:
        # ... (існуючий код) ...
        if data.get("model_id") is None:
            logger.error("model_id не надано для створення запису 'cars'.")
            return None

        sql_cars = """
                   INSERT INTO cars (model_id, production_year, body_type, transmission, drive)
                   VALUES (%s, %s, %s, %s, %s)
                   """
        car_params = (
            data.get("model_id"),
            data.get("production_year"),
            data.get("body_type_str"),
            data.get("transmission_str"),
            data.get("drive_str"),
        )
        cursor.execute(sql_cars, car_params)
        car_id = cursor.lastrowid
        logger.info(f"Створено запис в 'cars' з ID: {car_id}")

        sql_powertrains = """
                          INSERT INTO powertrains (car_id, fuel_type_id, mileage)
                          VALUES (%s, %s, %s)
                          """
        powertrain_params = (
            car_id,
            data.get("fuel_type_id"),
            data.get("mileage_km")
        )
        cursor.execute(sql_powertrains, powertrain_params)
        powertrain_id = cursor.lastrowid
        logger.info(f"Створено запис в 'powertrains' з ID: {powertrain_id} для car_id: {car_id}")

        fuel_type_key = data.get("raw_fuel_type", "").lower()

        if fuel_type_key in ('petrol', 'diesel', 'lpg', 'cng', 'ethanol', 'gasoline'):
            if data.get("engine_volume_cc") is not None:
                sql_ice_details = """
                                  INSERT INTO ice_powertrain_details (powertrain_id, engine_volume_cc)
                                  VALUES (%s, %s)
                                  """
                ice_params = (powertrain_id, data.get("engine_volume_cc"))
                cursor.execute(sql_ice_details, ice_params)
                logger.info(f"Створено запис в 'ice_powertrain_details' для powertrain_id: {powertrain_id}")
            else:
                logger.warning(f"Для ДВЗ (powertrain_id: {powertrain_id}) не надано engine_volume_cc.")
        elif fuel_type_key == 'electric':
            if data.get("battery_capacity_kwh") is not None:
                sql_electric_details = """
                                       INSERT INTO electric_powertrain_details (powertrain_id, battery_capacity_kwh)
                                       VALUES (%s, %s)
                                       """
                electric_params = (powertrain_id, data.get("battery_capacity_kwh"))
                cursor.execute(sql_electric_details, electric_params)
                logger.info(f"Створено запис в 'electric_powertrain_details' для powertrain_id: {powertrain_id}")
            else:
                logger.warning(f"Для EV (powertrain_id: {powertrain_id}) не надано battery_capacity_kwh.")
        return car_id


    @staticmethod
    def delete_car_and_dependencies(car_id: int, cursor: Any) -> bool:
        # ... (існуючий код) ...
        cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            logger.info(
                f"Видалено запис з 'cars' (ID: {car_id}) та пов'язані дані силової установки каскадно.")
            return True
        logger.warning(f"Автомобіль з car_id {car_id} не знайдено для видалення з таблиці 'cars' (або вже видалено).")
        return False

    @staticmethod
    def update_car_fields(car_id: int, update_data: Dict[str, Any], cursor: Any) -> bool:
        if not update_data:
            logger.info(f"Немає даних для оновлення в 'cars' для car_id {car_id}.")
            return False

        allowed_fields = {'production_year', 'body_type', 'transmission', 'drive'}

        set_clauses = []
        params = []

        for key, value in update_data.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = %s")
                params.append(value)
            else:
                logger.warning(f"CarRepository: Спроба оновити недозволене або невідоме поле '{key}' в 'cars'.")


        if not set_clauses:
            logger.info(f"Немає дозволених полів для оновлення в 'cars' для car_id {car_id}.")
            return False

        sql = f"UPDATE cars SET {', '.join(set_clauses)} WHERE id = %s"
        params.append(car_id)

        try:
            cursor.execute(sql, tuple(params))
            logger.info(f"Оновлено 'cars' для car_id {car_id}, змінено рядків: {cursor.rowcount}. Дані: {update_data}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Помилка оновлення полів для car_id {car_id} в 'cars': {e}", exc_info=True)
            raise # Перекидаємо помилку для обробки транзакцією

    @staticmethod
    def update_powertrain_mileage(powertrain_id: int, mileage: int, cursor: Any) -> bool:
        if mileage is None or mileage < 0 : # Пробіг може бути 0
            logger.warning(f"Некоректне значення пробігу ({mileage}) для powertrain_id {powertrain_id}. Оновлення скасовано.")
            return False

        sql = "UPDATE powertrains SET mileage = %s WHERE id = %s"
        try:
            cursor.execute(sql, (mileage, powertrain_id))
            logger.info(f"Оновлено пробіг до {mileage} для powertrain_id {powertrain_id}, змінено рядків: {cursor.rowcount}.")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Помилка оновлення пробігу для powertrain_id {powertrain_id}: {e}", exc_info=True)
            raise

    @staticmethod
    def update_powertrain_details(powertrain_id: int, details_data: Dict[str, Any], cursor: Any) -> bool:
        raw_fuel_type = details_data.get('raw_fuel_type', '').lower()
        updated = False # Флаг, чи відбулись якісь зміни

        # Оновлення для ДВЗ
        if raw_fuel_type in ('petrol', 'diesel', 'lpg', 'cng', 'ethanol', 'gasoline'):
            engine_volume_cc = details_data.get('engine_volume_cc') # Може бути None для скидання

            # Перевіряємо, чи існує запис
            cursor.execute("SELECT powertrain_id FROM ice_powertrain_details WHERE powertrain_id = %s", (powertrain_id,))
            existing_ice_detail = cursor.fetchone()

            if engine_volume_cc is not None:
                if existing_ice_detail:
                    sql_ice = "UPDATE ice_powertrain_details SET engine_volume_cc = %s WHERE powertrain_id = %s"
                else:
                    # Якщо запису немає, а об'єм є, створюємо його
                    sql_ice = "INSERT INTO ice_powertrain_details (engine_volume_cc, powertrain_id) VALUES (%s, %s)"

                try:
                    cursor.execute(sql_ice, (engine_volume_cc, powertrain_id))
                    logger.info(f"ICE details для powertrain_id {powertrain_id} {'оновлено' if existing_ice_detail else 'створено'} з engine_volume_cc: {engine_volume_cc}.")
                    updated = True # Була спроба оновлення/вставки
                except Exception as e:
                    logger.error(f"Помилка оновлення/вставки ICE details для powertrain_id {powertrain_id}: {e}", exc_info=True)
                    raise
            elif existing_ice_detail: # engine_volume_cc is None, але запис існує - скидаємо на NULL або видаляємо
                sql_ice_null = "UPDATE ice_powertrain_details SET engine_volume_cc = NULL WHERE powertrain_id = %s"
                # Або: sql_ice_delete = "DELETE FROM ice_powertrain_details WHERE powertrain_id = %s"
                cursor.execute(sql_ice_null, (powertrain_id,))
                logger.info(f"ICE details для powertrain_id {powertrain_id} встановлено engine_volume_cc в NULL.")
                updated = True

            # Якщо це був електро, і тепер стає ДВЗ, треба видалити запис з electric_powertrain_details
            cursor.execute("DELETE FROM electric_powertrain_details WHERE powertrain_id = %s", (powertrain_id,))
            if cursor.rowcount > 0:
                logger.info(f"Видалено запис з electric_powertrain_details для powertrain_id {powertrain_id} при зміні типу на ДВЗ.")
                updated = True


        # Оновлення для електромобілів
        elif raw_fuel_type == 'electric':
            battery_capacity_kwh = details_data.get('battery_capacity_kwh') # Може бути None для скидання

            cursor.execute("SELECT powertrain_id FROM electric_powertrain_details WHERE powertrain_id = %s", (powertrain_id,))
            existing_electric_detail = cursor.fetchone()

            if battery_capacity_kwh is not None:
                if existing_electric_detail:
                    sql_electric = "UPDATE electric_powertrain_details SET battery_capacity_kwh = %s WHERE powertrain_id = %s"
                else:
                    sql_electric = "INSERT INTO electric_powertrain_details (battery_capacity_kwh, powertrain_id) VALUES (%s, %s)"
                try:
                    cursor.execute(sql_electric, (battery_capacity_kwh, powertrain_id))
                    logger.info(f"Electric details для powertrain_id {powertrain_id} {'оновлено' if existing_electric_detail else 'створено'} з battery_capacity_kwh: {battery_capacity_kwh}.")
                    updated = True
                except Exception as e:
                    logger.error(f"Помилка оновлення/вставки Electric details для powertrain_id {powertrain_id}: {e}", exc_info=True)
                    raise
            elif existing_electric_detail: # battery_capacity_kwh is None, але запис існує
                sql_electric_null = "UPDATE electric_powertrain_details SET battery_capacity_kwh = NULL WHERE powertrain_id = %s"
                # Або: sql_electric_delete = "DELETE FROM electric_powertrain_details WHERE powertrain_id = %s"
                cursor.execute(sql_electric_null, (powertrain_id,))
                logger.info(f"Electric details для powertrain_id {powertrain_id} встановлено battery_capacity_kwh в NULL.")
                updated = True

            # Якщо це був ДВЗ, і тепер стає електро, треба видалити запис з ice_powertrain_details
            cursor.execute("DELETE FROM ice_powertrain_details WHERE powertrain_id = %s", (powertrain_id,))
            if cursor.rowcount > 0:
                logger.info(f"Видалено запис з ice_powertrain_details для powertrain_id {powertrain_id} при зміні типу на електро.")
                updated = True

        else:
            logger.warning(f"Невідомий raw_fuel_type '{raw_fuel_type}' для powertrain_id {powertrain_id}. Оновлення деталей силової установки не виконано.")

        return updated # Повертає True, якщо була спроба якоїсь зміни