import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.utils.ev_utils import find_battery_capacity
from app.utils.logger_config import logger


class AutoScout24Parser:
    _searched_cars_count = 0

    def __init__(self, base_url, make, model, pricefrom, priceto, fregfrom, fregto, kmfrom, kmto, cy, fuel,
                 page_count=2,
                 ):
        self.base_url = base_url
        self.make = make
        self.model = model
        self.pricefrom = pricefrom
        self.priceto = priceto
        self.fregfrom = fregfrom
        self.fregto = fregto
        self.kmfrom = kmfrom
        self.kmto = kmto
        self.cy = cy
        self.fuel = fuel
        self.page_count = page_count

    def _configure_url(self) -> tuple[dict[str, str | int], str]:
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
        if self.make:
            path += f"/{self.make.lower()}"
        if self.model:
            path += f"/{self.model.lower()}"

        return params, path

    def parse(self):
        all_parsed_cars_data = []
        params, path = self._configure_url()
        page = 1
        while page <= self.page_count:
            params["page"] = str(page)
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            url = self.base_url + path + "?" + query
            logger.info(f"Parsing page {page}: {url}")

            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                response.raise_for_status()
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
                    detail_url = self.base_url + link_tag["href"]
                    details_resp = requests.get(detail_url, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(details_resp.text, "html.parser")

                    short_data = detail_soup.find("script", type="application/ld+json")
                    detailed_data = detail_soup.find("script", id="__NEXT_DATA__", type="application/json")
                    if not detailed_data:
                        logger.warning("JSON __NEXT_DATA__ не знайдено.")
                        continue

                    try:
                        ld_data = json.loads(short_data.string)
                        next_data = json.loads(detailed_data.string)
                        listing = next_data["props"]["pageProps"]["listingDetails"]
                        vehicle = listing.get("vehicle", {})

                        identifier = listing.get("id")
                        brand = vehicle.get("make")
                        model = vehicle.get("model")
                        year = self._parse_production_year(vehicle, detail_soup)
                        mileage = vehicle.get("mileageInKmRaw")
                        fuel = vehicle.get("fuelCategory", {}).get("formatted")

                        battery_capacity_kwh = None
                        if fuel == "electric":
                            battery_capacity_kwh = find_battery_capacity(brand, model, year)

                        engine_volume = vehicle.get("rawDisplacementInCCM")
                        price = ld_data.get("offers", {}).get("price")
                        currency = ld_data.get("offers", {}).get("priceCurrency")
                        transmission = vehicle.get("transmissionType")
                        drive = vehicle.get("driveTrain")

                        country_code = listing.get("location", {}).get("countryCode")
                        body = vehicle.get("bodyType")

                    except Exception as e:
                        logger.error("Неможливо обробити JSON структуру:", e)
                        continue

                    car_data = {
                        "identifier": identifier,
                        "link_to_offer": detail_url,
                        "price": price,
                        "currency": currency,
                        "country_code": country_code,
                        "make": brand,
                        "model": model,
                        "year": year,
                        "body_type": body,
                        "fuel_type_key": fuel,
                        "engine_volume": engine_volume,
                        "battery_capacity_kwh": battery_capacity_kwh,
                        "transmission": transmission,
                        "drive": drive,
                        "mileage": mileage,
                    }
                    logger.info(f"Отримано оголошення:{car_data}")

                    all_parsed_cars_data.append(car_data)

                except Exception as e:
                    logger.error(f"Помилка при обробці авто: {e}")

            page += 1

        return all_parsed_cars_data

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
