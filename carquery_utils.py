import requests

from functools import lru_cache
from logger_config import logger

@lru_cache(maxsize=1)
def get_all_makes():
    try:
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/Passenger%20Car?format=json"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        results = resp.json().get("Results", [])
        makes = []
        for m in results:
            name = m.get("MakeName")
            if name:
                make_id = name.lower().replace(" ", "-")
                makes.append({"make_id": make_id, "make_display": name})
        return makes
    except Exception as e:
        logger.error(f"Error fetching passenger-car makes from vPIC: {e}")
        return []

@lru_cache(maxsize=128)
def get_models_for_make(make_id):

    make_name = make_id.replace('-', ' ').title()
    try:
        resp = requests.get(
            f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{make_name}?format=json",
            timeout=5
        )
        resp.raise_for_status()
        results = resp.json().get("Results", [])
        seen = set()
        models = []
        for m in results:
            name = m.get('Model_Name')
            if name and name not in seen:
                seen.add(name)
                models.append({'model_name': name})
        return models
    except Exception as e:
        logger.error(f"Error fetching models for {make_name} from vPIC: {e}")
        return []