from typing import Optional

import requests
from datetime import datetime


def get_eur_to_uah_rate():
    try:
        response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&json")
        if response.status_code == 200:
            data = response.json()
            return float(data[0]["rate"])
        else:
            print("[ERROR] Не вдалося отримати курс євро від НБУ. Статус:", response.status_code)
            return 41  # fallback
    except Exception as e:
        print("[ERROR] Виняток при запиті до НБУ:", e)
        return 41


def calculate_customs(year: int, engine_volume: float, engine_type: str, price_eur: float) -> Optional[float] :
    if year is None or engine_volume is None or engine_type is None or price_eur is None:
        print("[ERROR] Невалідні вхідні дані для розрахунку митних платежів")
        return None

    current_year = datetime.now().year
    car_age = max(1, current_year - year)
    rate = get_eur_to_uah_rate()

    engine_type = engine_type.lower()
    if engine_type in ['electricity', 'electric', 'bev', 'e']:
        return 0.0  # Повністю звільнено

    elif engine_type in ['diesel', 'd']:
        base_rate = 75
    else:
        base_rate = 50  # Для бензину та інших

    excise = base_rate * engine_volume * car_age
    import_duty = 0.1 * (price_eur * rate)
    vat = 0.2 * ((price_eur * rate) + excise + import_duty)

    total = excise + import_duty + vat
    return round(total, 2)
