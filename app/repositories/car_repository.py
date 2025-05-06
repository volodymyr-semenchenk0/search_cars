from app.db import execute_query, execute_modify
from app.utils.logger_config import logger


def _car_exists(identifier: str) -> bool:
    rows = execute_query(
        "SELECT 1 FROM cars WHERE identifier=%s LIMIT 1",
        (identifier,)
    )
    return bool(rows)


def save_car_to_db(car_data: dict):
    identifier = car_data.get("identifier")

    if _car_exists(identifier):
        logger.info(
            f"Авто вже існує в базі: {car_data.get('make')}, "
            f"{car_data.get('model')}, {car_data.get('year')}, {car_data.get('price')}"
        )
        return

    insert_query = (
        "INSERT INTO cars (identifier, make, model, year, body_type, fuel_type, engine_volume, "
        "battery_capacity_kwh, transmission, drive, mileage, country, price, customs_uah, "
        "final_price_uah, link, source) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    params = (
        identifier,
        car_data.get("make"),
        car_data.get("model"),
        car_data.get("year"),
        car_data.get("body_type"),
        car_data.get("fuel_type"),
        car_data.get("engine_volume"),
        car_data.get("battery_capacity_kwh"),
        car_data.get("transmission"),
        car_data.get("drive"),
        car_data.get("mileage"),
        car_data.get("country"),
        car_data.get("price"),
        car_data.get("customs_uah"),
        car_data.get("final_price_uah"),
        car_data.get("link"),
        car_data.get("source")
    )

    try:
        execute_modify(insert_query, params)
    except Exception as e:
        logger.error(f"Не вдалося зберегти авто: {e}")


def get_all_cars() -> list[dict]:
    """
    Повертає всі автомобілі з бази у форматі list[dict].
    """
    query = (
        "SELECT brand, model, year, fuel_type, engine_volume, country, "
        "price, customs_uah, final_price_uah, link "
        "FROM cars"
    )
    return execute_query(query)
