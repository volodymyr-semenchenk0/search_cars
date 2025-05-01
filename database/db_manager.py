
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="qwerty123",
        database="cars_db"
    )

def save_car_to_db(car_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = (
        "INSERT INTO cars (brand, model, year, body_type, engine_type, engine_volume, "
        "transmission, drive, mileage, country, price, customs_uah, final_price_uah, link, source) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    params = (
        car_data.get("brand"),
        car_data.get("model"),
        car_data.get("year"),
        car_data.get("body_type"),
        car_data.get("engine_type"),
        car_data.get("engine_volume"),
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

    cursor.execute(insert_query, params)
    conn.commit()
    conn.close()


def get_all_cars():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT brand, model, year, engine_type, engine_volume, country, price, customs_uah, final_price_uah, link FROM cars")
    cars = cursor.fetchall()
    conn.close()
    return cars

def get_filtered_cars(brand, max_price, year_from, year_to):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT brand, model, year, engine_type, engine_volume, country, price, customs_uah, final_price_uah, link FROM cars WHERE 1=1"
    params = []

    if brand:
        query += " AND brand LIKE %s"
        params.append(f"%{brand}%")
    if max_price:
        query += " AND price <= %s"
        params.append(max_price)
    if year_from:
        query += " AND year >= %s"
        params.append(year_from)
    if year_to:
        query += " AND year <= %s"
        params.append(year_to)

    cursor.execute(query, params)
    cars = cursor.fetchall()
    conn.close()
    return cars
