from datetime import datetime

def get_years_list():
    return list(range(1988, datetime.now().year + 1))[::-1]

COUNTRY_NAMES = {
    "DE": "Німеччина",
    "AT": "Австрія",
    "BE": "Бельгія",
    "ES": "Іспанія",
    "FR": "Франція",
    "IT": "Італія",
    "LU": "Люксембург",
    "NL": "Нідерланди"
}

PRICE_OPTIONS = [
    500, 1000, 1500, 2000, 2500, 3000, 4000, 5000,
    6000, 7000, 8000, 9000, 10000, 12500, 15000,
    17500, 20000, 25000, 30000, 40000, 50000,
    75000, 100000
]

MILEAGE_OPTIONS = [
    2500, 5000, 10000, 20000, 30000, 40000, 50000,
    60000, 70000, 80000, 90000, 100000, 125000,
    150000, 175000, 200000
]


COUNTRY_CODES = {
    "Німеччина": "D",
    "Австрія": "A",
    "Бельгія": "B",
    "Іспанія": "E",
    "Франція": "F",
    "Італія": "I",
    "Люксембург": "L",
    "Нідерланди": "NL"
}


FUEL_TYPES = {
    "gasoline": {
        "label": "Бензин",
        "code": "B"
    },
    "diesel": {
        "label": "Дизель",
        "code": "D"
    },
    "electric": {
        "label": "Електро",
        "code": "E"
    },
    "electric/gasoline": {
        "label": "Електро/Бензин",
        "code": "2"
    },
    "electric/diesel": {
        "label": "Електро/Дизель",
        "code": "3"
    },
    "lpg": {
        "label": "Газ",
        "code": "L"
    },
    "ethanol": {
        "label": "Газ (Етанол)",
        "code": "M"
    },
    "cng": {
        "label": "Газ (Метанол)",
        "code": "C"
    },
    "hydrogen": {
        "label": "Водень",
        "code": "H"
    },
    "others": {
        "label": "Інше",
        "code": "O"
    }
}

def get_fuel_label(key: str) -> str:
    return FUEL_TYPES.get(key, {}).get('label', key)

def get_fuel_code(key: str) -> str:
    return FUEL_TYPES.get(key, {}).get('code', key)

BODY_TYPES = {
    "sedan": "Седан",
    "hatchback": "Хетчбек",
    "coupe": "Купе",
    "suv": "Позашляховик",
    "convertible": "Кабріолет",
    "wagon": "Універсал",
    "van": "Мінівен",
    "pickup": "Пікап",
}

TRANSMISSIONS = {
    "manual": "Механічна",
    "automatic": "Автоматична",
    "semiautomatic": "Напівавтоматична"
}

DRIVE_TYPES = {
    "fwd": "Передній",
    "rwd": "Задній",
    "awd": "Повний",
    "4wd": "Повний",
    "front": "Передній",
    "rear": "Задній",
    "all": "Повний"
}
