# common.py

def format_car_price(price):
    """Форматує ціну автомобіля."""
    return f"{price} грн"

def format_car_year(year):
    """Форматує рік автомобіля."""
    return f"{year}"

def format_mileage(mileage):
    """Форматує пробіг автомобіля."""
    return f"{mileage} км"

def format_car_link(link):
    """Форматує посилання на автомобіль."""
    return f"Посилання: {link}"

# Можна додавати інші допоміжні функції, які будуть використовуватися в кількох частинах програми.


COUNTRY_NAMES = {
    "d": "Німеччина",
    "a": "Австрія",
    "b": "Бельгія",
    "e": "Іспанія",
    "f": "Франція",
    "i": "Італія",
    "l": "Люксембург",
    "nl": "Нідерланди"
}

# 🇺🇦 Українські переклади для відображення

ENGINE_TYPES = {
    "petrol": "Бензин",
    "gasoline": "Бензин",
    "diesel": "Дизель",
    "electric": "Електро",
    "electric/gasoline": "Гібрид",
    "lpg": "Газ",
    "hybrid": "Гібрид",
}

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
