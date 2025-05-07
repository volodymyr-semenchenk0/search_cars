import os
from contextlib import closing

from dotenv import load_dotenv
from mysql.connector import pooling, Error

from app.utils.logger_config import logger

load_dotenv()
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=int(os.getenv('DB_POOL_SIZE', 5)),
    **DB_CONFIG
)


def get_db_connection():
    return pool.get_connection()


def execute_query(query: str, params: tuple = None) -> list:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def execute_modify(query: str, params: tuple = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    except Error as e:
        conn.rollback()
        logger.error(f"Error executing modify: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
