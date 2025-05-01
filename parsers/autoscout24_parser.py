
import requests
from bs4 import BeautifulSoup
from database.db_manager import save_car_to_db
from customs import calculate_customs

BASE_URL = "https://www.autoscout24.com"

# Мапи кодів AutoScout24
FUEL_CODES = {
    "petrol": "P", "diesel": "D", "electric": "E", "electric/gasoline": "H", "lpg": "L"
}
BODY_CODES = {
    "sedan": "1", "hatchback": "2", "coupe": "3", "suv": "6", "convertible": "5", "wagon": "7",
    "van": "8", "pickup": "10"
}
TRANSMISSION_CODES = {
    "automatic": "A", "manual": "M", "semiautomatic": "S"
}
DRIVE_CODES = {
    "fwd": "fwd", "rwd": "rwd", "awd": "awd", "4wd": "4wd"
}

def safe_int(value):
    try:
        return int(value)
    except:
        return None

def parse_autoscout24(brand=None, model=None, year_from=None, year_to=None,
                      mileage=None, fuel=None, body=None, priceto=None,
                      countries=None, transmission=None, drive=None, country_code=None):
    params = {
        "sort": "standard",
        "desc": "0",
        "ustate": "N,U",
        "size": "20",
        "atype": "C",
        "damaged_listing": "exclude",
        "powertype": "kw"
    }

    if year_from:
        params["yearfrom"] = year_from
    if year_to:
        params["fregto"] = year_to
    if mileage:
        params["kmto"] = mileage
    if fuel and fuel in FUEL_CODES:
        params["fuel"] = FUEL_CODES[fuel]
    if body and body in BODY_CODES:
        params["body"] = BODY_CODES[body]
    if priceto:
        params["priceto"] = priceto
    if country_code:
        params["cy"] = country_code
    elif country_code:
        params["cy"] = country_code
    if transmission and transmission in TRANSMISSION_CODES:
        params["gear"] = TRANSMISSION_CODES[transmission]
        params["transmission"] = transmission
    if drive and drive in DRIVE_CODES:
        params["drive"] = DRIVE_CODES[drive]

    path = "/lst"
    if brand:
        path += f"/{brand.lower()}"
        if model:
            path += f"/{model.lower()}"

    page = 1
    while True:
        params["page"] = str(page)
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = BASE_URL + path + "?" + query

        print(f"[INFO] Парсинг сторінки {page}: {url}")

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        car_elements = soup.find_all("article", class_="cldt-summary-full-item")
        if not car_elements:
            print("[INFO] Більше сторінок немає. Завершено.")
            break

        print(f"[INFO] Знайдено {len(car_elements)} авто на сторінці {page}")

        for car in car_elements:
            try:
                title_link = car.select_one('a[href^="/offers"]')
                if not title_link:
                    continue
                spans = title_link.find_all("span")
                if len(spans) < 2:
                    continue
                brand_text = spans[0].get_text(strip=True)
                model_text = spans[1].get_text(strip=True)
                if len(spans) > 2:
                    version = spans[2].get_text(strip=True)
                    model_text += f" {version}"

                price_tag = car.select_one('[data-testid="regular-price"]')
                if not price_tag:
                    continue
                price_str = price_tag.get_text(strip=True).replace("€", "").replace(",", "").strip()
                price = float(price_str)

                link = BASE_URL + title_link["href"]

                year = None
                mileage_val = None
                engine_type = None
                transmission_val = None

                details = car.select('[data-testid^="VehicleDetails-"]')
                for d in details:
                    text = d.get_text(strip=True)
                    dt = d["data-testid"]
                    if dt == "VehicleDetails-mileage_road":
                        clean = text.replace("km", "").replace(",", "").strip()
                        mileage_val = safe_int(clean)
                    elif dt == "VehicleDetails-calendar":
                        parts = text.split("/")
                        if len(parts) == 2:
                            year = safe_int(parts[1])
                    elif dt == "VehicleDetails-gas_pump":
                        engine_type = text.lower()
                    elif dt == "VehicleDetails-transmission":
                        transmission_val = text.lower()

                if year is None:
                    year = 2016
                if mileage_val is None:
                    mileage_val = 120000
                if engine_type is None:
                    engine_type = "petrol"
                if transmission_val is None:
                    transmission_val = "manual"

                engine_volume = 1.6
                drive_val = "FWD"
                country_attr = car.get("data-listing-country", "d")
                body_type = "sedan"

                customs_uah = calculate_customs(year, engine_volume, engine_type, price)
                final_price = round(price * 41 + customs_uah, 2)

                car_data = {
                    "brand": brand_text,
                    "model": model_text,
                    "year": year,
                    "body_type": body_type,
                    "engine_type": engine_type,
                    "engine_volume": engine_volume,
                    "transmission": transmission_val,
                    "drive": drive_val,
                    "mileage": mileage_val,
                    "country": country_attr,
                    "price": price,
                    "customs_uah": customs_uah,
                    "final_price_uah": final_price,
                    "link": link,
                    "source": "AutoScout24"
                }

                save_car_to_db(car_data)
            except Exception as e:
                print("[ERROR] Помилка при обробці авто:", e)

        page += 1
