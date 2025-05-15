from app.db import execute_query, execute_modify
from app.repositories.source_repository import SourceRepository
from app.utils.logger_config import logger

class CarRepository:
    @staticmethod
    def get_all_cars() -> list:
        sql = ("SELECT id, make, model, year, body_type, fuel_type, "
               + "engine_volume, battery_capacity_kwh, transmission, drive, mileage, country, price, customs, final_price_uah, link, source "
               + "FROM cars")
        return execute_query(sql)

    @staticmethod
    def get_car_by_id(car_id: int) -> dict:
        sql = ("SELECT id, make, model, year, body_type, fuel_type, engine_volume, battery_capacity_kwh, "
               "transmission, drive, mileage, country, price, customs, final_price_uah, link, source "
               "FROM cars WHERE id = %s")
        rows = execute_query(sql, (car_id,))
        return rows[0] if rows else None

    @staticmethod
    def car_exists(identifier: str) -> bool:
        sql = "SELECT 1 FROM cars WHERE identifier = %s LIMIT 1"
        rows = execute_query(sql, (identifier,))
        return bool(rows)

    @staticmethod
    def save_car(car: dict) -> bool:
        identifier = car.get("identifier")
        if CarRepository.car_exists(identifier):
            logger.info(f"Car with identifier '{identifier}' already exists. Skipping save.")
            return False

        source_id = car.get("source_id")

        sql = (
            "INSERT INTO cars (identifier, make, model, year, body_type, fuel_type, "
            "engine_volume, battery_capacity_kwh, transmission, drive, mileage, country, "
            "price, customs, final_price_uah, link, source_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )


        params = (
            identifier,
            car.get("make"),
            car.get("model"),
            car.get("year"),
            car.get("body_type"),
            car.get("fuel_type"),
            car.get("engine_volume"),
            car.get("battery_capacity_kwh"),
            car.get("transmission"),
            car.get("drive"),
            car.get("mileage"),
            car.get("country"),
            car.get("price"),
            car.get("customs"),
            car.get("final_price_uah"),
            car.get("link"),
            source_id
        )

        try:
            rows_affected = execute_modify(sql, params)
            return rows_affected == 1
        except Exception as e:
            logger.error(f"Error saving car with identifier '{identifier}' to database: {e}")
            return False


    @staticmethod
    def update_car(car_id: int, update_fields: dict) -> bool:
        if not update_fields:
            return False
        set_clause = ", ".join(f"{key} = %s" for key in update_fields.keys())
        params = list(update_fields.values()) + [car_id]
        sql = f"UPDATE cars SET {set_clause} WHERE id = %s"
        return execute_modify(sql, tuple(params)) == 1

    @staticmethod
    def delete_car(car_id: int) -> bool:
        sql = "DELETE FROM cars WHERE id = %s"
        return execute_modify(sql, (car_id,)) == 1

    @staticmethod
    def get_filtered_cars(
            make: str = None,
            model: str = None,
            fuel_type: str = None,
            year: int = None,
            country: str = None,
            sort: str = None
    ) -> list:
        query = (
            "SELECT id, make, model, year, body_type, fuel_type, engine_volume, "
            "battery_capacity_kwh, transmission, drive, mileage, country, price, customs, "
            "final_price_uah, link, source, created_at "
            "FROM cars"
        )
        where_clauses = []
        params = []
        if make:
            where_clauses.append("make = %s")
            params.append(make)
        if model:
            where_clauses.append("model = %s")
            params.append(model)
        if fuel_type:
            where_clauses.append("fuel_type = %s")
            params.append(fuel_type)
        if year:
            where_clauses.append("year = %s")
            params.append(year)
        if country:
            where_clauses.append("country = %s")
            params.append(country)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        # Сортування
        if sort == 'price_asc':
            query += " ORDER BY price ASC"
        elif sort == 'price_desc':
            query += " ORDER BY price DESC"
        elif sort == 'oldest':
            query += " ORDER BY created_at ASC"
        else:
            query += " ORDER BY created_at DESC"
        return execute_query(query, tuple(params))

    @staticmethod
    def get_cars_by_ids(car_ids: list[int]) -> list[dict]:
        if not car_ids:
            return []
        placeholders = ','.join(['%s'] * len(car_ids))
        sql = ("SELECT id, make, model, year, body_type, fuel_type, engine_volume, battery_capacity_kwh,"
               " transmission, drive, mileage, country, price, customs, final_price_uah, link, source"
               f" FROM cars WHERE id IN ({placeholders})")
        rows = execute_query(sql, tuple(car_ids))
        return rows
