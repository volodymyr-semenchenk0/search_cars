# app/repositories/car_repository.py
from typing import Optional, Dict, Any

from app.utils.logger_config import logger


class CarRepository:
    @staticmethod
    def create_car_with_powertrain(data: Dict[str, Any], cursor: Any) -> Optional[int]:
        """
        Створює запис в 'cars', 'powertrains' та деталях силової установки (ice/electric).
        Приймає відкритий курсор бази даних для виконання в межах існуючої транзакції.
        Повертає car_id.
        """
        if data.get("model_id") is None:
            logger.error("model_id не надано для створення запису 'cars'.")
            # Транзакція буде відкочена на вищому рівні, якщо цей метод викликається з create_full_offer
            return None

        sql_cars = """
                   INSERT INTO cars (model_id, production_year, body_type, transmission, drive)
                   VALUES (%s, %s, %s, %s, %s) \
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
                          VALUES (%s, %s, %s) \
                          """
        powertrain_params = (
            car_id,
            data.get("fuel_type_id"),
            data.get("mileage_km")
        )
        cursor.execute(sql_powertrains, powertrain_params)
        powertrain_id = cursor.lastrowid
        logger.info(f"Створено запис в 'powertrains' з ID: {powertrain_id} для car_id: {car_id}")

        fuel_type_key = data.get("raw_fuel_type", "").lower()  # Змінено з raw_fuel_type_key

        if fuel_type_key in ('petrol', 'diesel', 'lpg', 'cng', 'ethanol', 'gasoline'):
            if data.get("engine_volume_cc") is not None:
                sql_ice_details = """
                                  INSERT INTO ice_powertrain_details (powertrain_id, engine_volume_cc)
                                  VALUES (%s, %s) \
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
                                       VALUES (%s, %s) \
                                       """
                electric_params = (powertrain_id, data.get("battery_capacity_kwh"))
                cursor.execute(sql_electric_details, electric_params)
                logger.info(f"Створено запис в 'electric_powertrain_details' для powertrain_id: {powertrain_id}")
            else:
                logger.warning(f"Для EV (powertrain_id: {powertrain_id}) не надано battery_capacity_kwh.")
        return car_id

    @staticmethod
    def delete_car_and_dependencies(car_id: int, cursor: Any) -> bool:
        """
        Видаляє автомобіль ('cars') та пов'язані з ним записи ('powertrains', 'ice_details', 'electric_details').
        Приймає відкритий курсор для виконання в межах транзакції.
        Передбачається, що залежні 'offers' вже видалені або будуть видалені окремо.
        """
        # `powertrains` має ON DELETE CASCADE від `cars`.
        # `ice_powertrain_details` та `electric_powertrain_details` мають ON DELETE CASCADE від `powertrains`.
        # Отже, достатньо видалити з `cars`.
        cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            logger.info(
                f"Видалено запис з 'cars' (ID: {car_id_to_delete}) та пов'язані дані силової установки каскадно.")
            return True
        logger.warning(f"Автомобіль з car_id {car_id} не знайдено для видалення з таблиці 'cars'.")
        return False

    # Методи вибірки, які повертають повну інформацію про авто (з JOIN-ами),
    # можуть залишитися тут або бути частиною OfferRepository, якщо вони завжди вибираються в контексті пропозицій.
    # Для чистоти, методи, що вибирають дані СПЕЦИФІЧНО для відображення пропозицій, краще перенести в OfferRepository.
    # Залишимо тут тільки ті, що стосуються вибірки саме авто, якщо такі будуть потрібні окремо.
    # Наразі, більшість ваших SELECT запитів були в контексті "пропозицій".
