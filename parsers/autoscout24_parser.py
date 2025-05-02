
import requests
from bs4 import BeautifulSoup
import json
from database.db_manager import save_car_to_db
from customs import calculate_customs

BASE_URL = "https://www.autoscout24.com"

def safe_int(value):
    try:
        return int(value)
    except:
        return None

def safe_float(value):
    try:
        return float(value)
    except:
        return None

def get_details_from_json_script(soup):
    script_tag = soup.find("script", type="application/ld+json")
    if not script_tag:
        return None
    try:
        data = json.loads(script_tag.string)
        return data
    except Exception as e:
        print("[ERROR] JSON parsing failed:", e)
        return None

def parse_autoscout24(brand=None, model=None, year_from=None, year_to=None,
                      mileage=None, fuel=None, body=None, priceto=None,
                      transmission=None, drive=None, country_code=None):

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
    if fuel:
        params["fuel"] = fuel
    if body:
        params["body"] = body
    if priceto:
        params["priceto"] = priceto
    if transmission:
        params["transmission"] = transmission
    if drive:
        params["drive"] = drive
    if country_code:
        params["cy"] = country_code

    path = "/lst"
    if brand:
        path += f"/{brand.lower()}"
        if model:
            path += f"/{model.lower()}"

    page = 1
    while True:
        if page > 2:
            break

        params["page"] = str(page)
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = BASE_URL + path + "?" + query
        print(f"[INFO] Parsing page {page}: {url}")

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        car_elements = soup.find_all("article", class_="cldt-summary-full-item", attrs={"data-source": "listpage_search-results"})
        if not car_elements:
            print("[INFO] No more listings or no results.")
            break

        for car in car_elements:
            try:
                link_tag = car.select_one('a[href^="/offers"]')
                if not link_tag:
                    continue
                detail_url = BASE_URL + link_tag["href"]

                detail_resp = requests.get(detail_url, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                json_data = get_details_from_json_script(detail_soup)
                if not json_data or "offers" not in json_data:
                    continue

                offer = json_data.get("offers")
                item = offer.get("itemOffered", {})

                identifier_val = item.get("identifier")
                brand_val = item.get("manufacturer")
                model_val = item.get("model")
                year_val = safe_int(item.get("productionDate", "").split("-")[0])
                mileage_val = safe_int(item.get("mileageFromOdometer", {}).get("value"))
                fuel_val = item.get("vehicleEngine", [{}])[0].get("fuelType")
                price_val = safe_float(offer.get("price"))
                transmission_val = item.get("vehicleTransmission")
                drive_val = item.get("driveWheelConfiguration")
                engine_volume = safe_float(item.get("vehicleEngine", [{}])[0].get("engineDisplacement", {}).get("value"))
                country_val = offer.get("offeredBy", {}).get("address", {}).get("addressCountry")
                body_val = item.get("bodyType")

                if not (brand_val and model_val and year_val and price_val):
                    continue

                customs_uah = calculate_customs(year_val, engine_volume or 1.6, fuel_val or "petrol", price_val)
                final_price = round(price_val * 41 + customs_uah, 2)

                car_data = {
                    "identifier": identifier_val,
                    "brand": brand_val,
                    "model": model_val,
                    "year": year_val,
                    "body_type": body_val,
                    "engine_type": fuel_val,
                    "engine_volume": engine_volume,
                    "transmission": transmission_val,
                    "drive": drive_val,
                    "mileage": mileage_val,
                    "country": country_val,
                    "price": price_val,
                    "customs_uah": customs_uah,
                    "final_price_uah": final_price,
                    "link": detail_url,
                    "source": "AutoScout24"
                }

                print("[DEBUG] Saving car:", car_data)
                save_car_to_db(car_data)

            except Exception as e:
                print("[ERROR] Failed to process listing:", e)

        page += 1
