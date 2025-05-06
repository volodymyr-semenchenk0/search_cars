# evdb_utils.py
import requests
from functools import lru_cache
from app.utils.logger_config import logger

# URL до 'raw' JSON файлу Open EV Data
RAW_URL = "https://raw.githubusercontent.com/KilowattApp/open-ev-data/master/data/ev-data.json"

@lru_cache(maxsize=1)
def load_ev_database():
    resp = requests.get(RAW_URL, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    # Якщо дані вкладені під 'data'
    if isinstance(j, dict) and 'data' in j and isinstance(j['data'], list):
        return j['data']
    if isinstance(j, list):
        return j
    logger.error(f"Unexpected JSON structure from EV database: {type(j)}")
    return []


def find_ev_specs(brand: str, model: str, year: int = None) -> list:

    data = load_ev_database()
    results = []
    for car in data:
        if car.get('brand', '').lower() == brand.lower() and car.get('model', '').lower() == model.lower():

            if year is None or car.get('release_year') == year:
                adapted = {
                    'brand': car.get('brand'),
                    'model': car.get('model'),
                    'year': car.get('release_year'),
                    'battery_capacity_kwh': car.get('usable_battery_size'),
                    'energy_consumption_wh_mi': car.get('energy_consumption', {}).get('average_consumption'),
                    'ac_charger_max_kw': car.get('ac_charger', {}).get('max_power'),
                    'dc_charger_max_kw': car.get('dc_charger', {}).get('max_power'),
                    'charging_curve': car.get('dc_charger', {}).get('charging_curve'),
                }
                results.append(adapted)
    return results
