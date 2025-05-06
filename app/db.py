# app/db.py
import mysql.connector
from contextlib import closing

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qwerty123',
    'database': 'cars_db',
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def execute_query(query: str, params: tuple = None):

    with closing(get_db_connection()) as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()

def execute_modify(query: str, params: tuple = None):

    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
