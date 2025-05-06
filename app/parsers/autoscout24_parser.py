import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.customs import CalculateCustoms
from app.db import save_car_to_db
from app.utils.logger_config import logger


class AutoScout24Parser:
    _BASE_URL = "https://www.autoscout24.com"
    brand, model, fregto, kmto, cy = None, None, None, None, None

    def __init__(self, brand, model, pricefrom, priceto, fregfrom, fregto, kmfrom, kmto, cy, fuel):
        self.brand = brand
        self.model = model
        self.pricefrom = pricefrom
        self.priceto = priceto
        self.fregfrom = fregfrom
        self.fregto = fregto
        self.kmfrom = kmfrom
        self.kmto = kmto
        self.cy = cy
        self.fuel = fuel

    @staticmethod
    def _configure_url(self):
        params = {
            "sort": "standard",
            "desc": "0",
            "ustate": "N,U",
            "size": "20",
            "atype": "C",
            "damaged_listing": "exclude",
        }

        if self.fregfrom:
            params["fregfrom"] = self.fregfrom
        if self.fregto:
            params["fregto"] = self.fregto
        if self.pricefrom:
            params["pricefrom"] = self.pricefrom
        if self.priceto:
            params["priceto"] = self.priceto
        if self.kmfrom:
            params["kmfrom"] = self.kmfrom
        if self.kmto:
            params["kmto"] = self.kmto
        if self.cy:
            params["cy"] = self.cy
        if self.fuel:
            params["fuel"] = self.fuel

        path = "/lst"
        if self.brand:
            path += f"/{self.brand.lower()}"
        if self.model:
            path += f"/{self.model.lower()}"

        return params, path

    def parse_autoscout24(self):

        params, path = self._configure_url(self)
        page = 1
        while True:
            # if page > 2:
            #     break

            params["page"] = str(page)
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            url = self._BASE_URL + path + "?" + query
            logger.info(f"Parsing page {page}: {url}")

            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                response.raise_for_status()  # Підніме помилку, якщо код не 2xx
            except requests.RequestException as e:
                logger.error(f"Не вдалося отримати сторінку {url}: {e}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            car_elements = soup.find_all("article", class_="cldt-summary-full-item",
                                         attrs={"data-source": "listpage_search-results"})
            if not car_elements:
                logger.error("No more listings or no results.")
                break

            for car in car_elements:
                try:
                    link_tag = car.select_one('a[href^="/offers"]')
                    if not link_tag:
                        continue
                    detail_url = self._BASE_URL + link_tag["href"]
                    details_resp = requests.get(detail_url, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(details_resp.text, "html.parser")

                    script_tag = detail_soup.find("script", id="__NEXT_DATA__", type="application/json")
                    if not script_tag:
                        logger.warning("JSON __NEXT_DATA__ не знайдено.")
                        continue

                    try:
                        next_data = json.loads(script_tag.string)
                        listing = next_data["props"]["pageProps"]["listingDetails"]
                        vehicle = listing.get("vehicle", {})

                        identifier_val = listing.get("id")
                        brand_val = vehicle.get("make")
                        model_val = vehicle.get("model")
                        year_val = self._safe_int(self._parse_production_year(vehicle, detail_soup))
                        mileage_val = self._safe_int(vehicle.get("mileageInKmRaw"))
                        fuel_val = vehicle.get("fuelCategory", {}).get("formatted").lower()

                        if fuel_val == "electric":
                            engine_volume = 0
                        else:
                            engine_volume = self._safe_float(vehicle.get("rawDisplacementInCCM"))

                        price_val = self._safe_float(listing.get("prices", {}).get("public", {}).get("priceRaw"))
                        transmission_val = vehicle.get("transmissionType")
                        drive_val = vehicle.get("driveTrain")

                        country_val = listing.get("location", {}).get("countryCode")
                        body_val = vehicle.get("bodyType")

                        # battery_capacity_kwh_val = None
                        # if fuel_val == "electric":
                        #     specs = find_ev_specs(brand_val, model_val, year_val)
                        #     battery_capacity_kwh_val = specs[0]['battery_capacity_kwh']

                    except Exception as e:
                        logger.error("Неможливо обробити JSON структуру:", e)
                        continue

                    customs_uah, final_price = None, None
                    calc_customs = CalculateCustoms().calculate(
                        price_val,
                        engine_volume,
                        year_val,
                        fuel_val,
                        battery_capacity_kwh=0.0,
                    )
                    if calc_customs is not None:
                        customs_uah = calc_customs.get("customs_value_uah")
                        final_price = calc_customs.get("total_uah")

                    car_data = {
                        "identifier": identifier_val,
                        "brand": brand_val,
                        "model": model_val,
                        "year": year_val,
                        "body_type": body_val,
                        "fuel_type": fuel_val,
                        "engine_volume": engine_volume,
                        # "battery_capacity_kwh": battery_capacity_kwh_val,
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

                    print("Збереження авто:", car_data)
                    save_car_to_db(car_data)

                except Exception as e:
                    logger.error(f"Помилка при обробці авто: {e}")

            page += 1

    @staticmethod
    def _parse_production_year(vehicle, detail_soup):
        year_val = vehicle.get("productionYear")

        if not year_val:
            year_val = vehicle.get("firstRegistrationDateRaw")
        else:
            return year_val

        if not year_val:
            script_tag = detail_soup.find("script", type="application/ld+json")
            if not script_tag:
                logger.warning("JSON не знайдено.")
                return None

            try:
                data = json.loads(script_tag.string)
                year_val = data.get("offers", {}).get("itemOffered", {}).get("productionDate")
            except Exception as e:
                logger.error("Неможливо розпарсити JSON:", e)
                return None

        if not year_val or not isinstance(year_val, str):
            return None

        try:
            return datetime.strptime(year_val, "%Y-%m-%d").year
        except ValueError:
            logger.warning("Неможливо обробити дату:", year_val)
            return None

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
