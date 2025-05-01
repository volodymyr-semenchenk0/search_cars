import mysql.connector
from database.db_manager import get_db_connection


class CarTableModel:
    def __init__(self):
        self.connection = get_db_connection()

    def get_all_cars(self):
        """Отримує всі автомобілі з бази даних."""
        query = "SELECT * FROM cars"
        cursor = self.connection.cursor()
        cursor.execute(query)
        cars = cursor.fetchall()
        cursor.close()
        return cars

    def get_filtered_cars(self, brand="", max_price="", year_from="", year_to=""):
        """Отримує автомобілі за фільтром (марка, ціна, рік)."""
        query = "SELECT * FROM cars WHERE 1"

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

        cursor = self.connection.cursor()
        cursor.execute(query, params)
        cars = cursor.fetchall()
        cursor.close()
        return cars

    def insert_car(self, brand, model, year, price, mileage, link, source):
        """Додає автомобіль до бази даних."""
        query = "INSERT INTO cars (brand, model, year, price, mileage, link, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = self.connection.cursor()
        cursor.execute(query, (brand, model, year, price, mileage, link, source))
        self.connection.commit()
        cursor.close()

    def delete_car(self, car_id):
        """Видаляє автомобіль за ID."""
        query = "DELETE FROM cars WHERE id = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (car_id,))
        self.connection.commit()
        cursor.close()

    def update_car(self, car_id, brand, model, year, price, mileage, link, source):
        """Оновлює дані автомобіля за ID."""
        query = "UPDATE cars SET brand = %s, model = %s, year = %s, price = %s, mileage = %s, link = %s, source = %s WHERE id = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (brand, model, year, price, mileage, link, source, car_id))
        self.connection.commit()
        cursor.close()

    def close_connection(self):
        """Закриває з'єднання з базою даних."""
        self.connection.close()
