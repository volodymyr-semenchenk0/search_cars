from typing import Optional

import requests
from datetime import datetime
from logger_config import logger

FALLBACK_RATE = 47


def get_eur_to_uah_rate():
    try:
        response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&json")
        if response.status_code == 200:
            data = response.json()
            return float(data[0]["rate"])
        else:
            logger.warning(f"Не вдалося отримати курс євро від НБУ. Статус:{response.status_code}")
            return FALLBACK_RATE
    except Exception as e:
        logger.warning(f"Виняток при запиті до НБУ: {e}")
        return FALLBACK_RATE


def calculate_customs(year: int, engine_volume: float, fuel_type: str, price_eur: float) -> Optional[float] :
    if year is None or engine_volume is None or fuel_type is None or price_eur is None:
        logger.warning("Невалідні вхідні дані для розрахунку митних платежів")
        return None

    current_year = datetime.now().year
    car_age = max(1, current_year - year)
    rate = get_eur_to_uah_rate()

    fuel_type = fuel_type.lower()
    if fuel_type in ['electricity', 'electric', 'bev', 'e']:
        return 0.0  # Повністю звільнено

    elif fuel_type in ['diesel', 'd']:
        base_rate = 75
    else:
        base_rate = 50  # Для бензину та інших

    excise = base_rate * engine_volume * car_age
    import_duty = 0.1 * (price_eur * rate)
    vat = 0.2 * ((price_eur * rate) + excise + import_duty)

    total = excise + import_duty + vat
    return round(total, 2)
