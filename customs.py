
def calculate_customs(year: int, engine_volume: float, engine_type: str, price_eur: float) -> float:
    import datetime

    current_year = datetime.datetime.now().year
    car_age = max(1, current_year - year)

    if engine_type.lower() == 'diesel':
        base_rate = 75
    else:  # бензин або інше
        base_rate = 50

    excise = base_rate * engine_volume * car_age
    nds = 0.2 * (price_eur * 41 + excise)  # умовний курс 1 EUR = 41 грн
    import_duty = 0.1 * (price_eur * 41)

    total = excise + nds + import_duty
    return round(total, 2)
