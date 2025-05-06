from functools import lru_cache
import requests
import logging

logger = logging.getLogger(__name__)

RAW_URL = "https://raw.githubusercontent.com/KilowattApp/open-ev-data/master/data/ev-data.json"

@lru_cache(maxsize=1)
def load_ev_database():
    try:
        resp = requests.get(RAW_URL, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        if isinstance(j, dict) and 'data' in j and isinstance(j['data'], list):
            return j['data']
        if isinstance(j, list):
            return j
        logger.error(f"Unexpected JSON structure from EV database: {type(j)}")
    except Exception as e:
        logger.error(f"Failed to load EV data: {e}")
    return []

def find_battery_capacity(brand: str, model: str = None, year: int = None) -> float | None:
    data = load_ev_database()
    brand = brand.lower().strip()
    model = model.lower().strip() if model else None

    for car in data:
        if car.get('brand', '').lower() != brand:
            continue

        if model and car.get('model', '').lower() != model:
            continue

        if year is not None and car.get('release_year') != year:
            continue

        return car.get('usable_battery_size')
    return None