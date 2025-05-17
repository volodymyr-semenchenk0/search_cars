import time

import requests

from app.db import get_db_connection  # Імпортуй функцію підключення


def fetch_all_makes():
    url = "https://www.carqueryapi.com/api/0.3/"
    params = {"cmd": "getMakes"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    data = resp.json()
    return data.get('Makes', [])


def fetch_models_for_make(make_id):
    url = "https://www.carqueryapi.com/api/0.3/"
    params = {"cmd": "getModels", "make": make_id}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    data = resp.json()
    return data.get('Models', [])


def save_make(conn, make):
    c = conn.cursor()
    c.execute(
        "INSERT IGNORE INTO car_makes (name, country_id) VALUES (%s, NULL)",
        (make['make_display'],)
    )
    conn.commit()
    c.execute("SELECT id FROM car_makes WHERE name = %s", (make['make_display'],))
    row = c.fetchone()
    c.close()
    return row[0] if row else None


def save_model(conn, model, make_db_id):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT IGNORE INTO car_models (make_id, name) VALUES (%s, %s)",
            (make_db_id, model['model_name'])
        )
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Cannot insert model '{model['model_name']}': {e}")
    finally:
        c.close()


def main():
    makes = fetch_all_makes()
    print(f"Знайдено марок: {len(makes)}")
    conn = get_db_connection()  # Підключення через твій db.py!
    try:
        for make in makes:
            make_db_id = save_make(conn, make)
            if not make_db_id:
                print(f"Помилка збереження марки {make['make_display']}")
                continue
            models = fetch_models_for_make(make['make_id'])
            print(f"{make['make_display']} ({make['make_id']}): {len(models)} моделей")
            for model in models:
                save_model(conn, model, make_db_id)
            time.sleep(0.5)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
