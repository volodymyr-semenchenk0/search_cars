from app.db import execute_query

from app.utils.logger_config import logger


def get_filtered_cars(
        make=None, model=None, fuel=None,
        year=None, country=None, sort=None
):
    # Базовий SELECT
    query = """
            SELECT identifier,
                   make,
                   model,
                   year,
                   fuel_type,
                   engine_volume,
                   battery_capacity_kwh,
                   transmission,
                   drive,
                   mileage,
                   country,
                   price,
                   customs_uah,
                   final_price_uah,
                   link,
                   created_at
            FROM cars \
            """
    where_clauses = []
    params = []

    # Додаємо WHERE‐умови тільки якщо є параметр
    if make:
        where_clauses.append("make = %s")
        params.append(make)
    if model:
        where_clauses.append("model = %s")
        params.append(model)
    if fuel:
        where_clauses.append("fuel_type = %s")
        params.append(fuel)
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
    else:  # default або 'latest'
        query += " ORDER BY created_at DESC"

    # Виконуємо і повертаємо список dict
    rows = execute_query(query, tuple(params))
    cars = [dict(row) for row in rows]
    logger.debug(f"Filtered {len(cars)} cars with {params}")
    return cars
