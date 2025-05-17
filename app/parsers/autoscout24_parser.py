import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pydantic_core._pydantic_core import ValidationError

from app.schemas.parsed_offer import ParsedCarOffer
from app.utils.ev_utils import find_battery_capacity
from app.utils.logger_config import logger


class AutoScout24Parser:
    _searched_cars_count = 0

    def __init__(self, base_url, make, model, pricefrom, priceto, fregfrom, fregto, kmfrom, kmto, cy, fuel,
                 page_count=1,
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

    def parse(self) -> list[ParsedCarOffer]:
        all_parsed_cars_data_models = []
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

                    ld_data = json.loads(short_data.string)
                    next_data = json.loads(detailed_data.string)
                    listing = next_data["props"]["pageProps"]["listingDetails"]
                    vehicle = listing.get("vehicle", {})

                    car_data_dict = {
                        "identifier": listing.get("id"),
                        "link_to_offer": detail_url,
                        "price": ld_data.get("offers", {}).get("price"),
                        "currency": ld_data.get("offers", {}).get("priceCurrency"),
                        "country_code": listing.get("location", {}).get("countryCode"),
                        "make": vehicle.get("make"),
                        "model": vehicle.get("model"),
                        "year": self._parse_production_year(vehicle, ld_data),
                        "body_type": vehicle.get("bodyType"),
                        "fuel_type": vehicle.get("fuelCategory", {}).get("formatted", "").lower() or None,
                        "engine_volume": vehicle.get("rawDisplacementInCCM"),
                        "battery_capacity_kwh": None,
                        "transmission": vehicle.get("transmissionType"),
                        "drive": vehicle.get("driveTrain"),
                        "mileage": vehicle.get("mileageInKmRaw"),
                    }

                    if car_data_dict["fuel_type"] == "electric":
                        car_data_dict["battery_capacity_kwh"] = find_battery_capacity(
                            car_data_dict["make"], car_data_dict["model"], car_data_dict["year"]
                        )

                    validated_offer = ParsedCarOffer(**car_data_dict)
                    all_parsed_cars_data_models.append(validated_offer)
                    logger.info(f"Успішно розпарсено та валідовано оголошення: {validated_offer.identifier}")


                except ValidationError as e:
                    logger.error(f"Помилка валідації даних для оголошення (URL: {detail_url}): {e.errors()}")
                except Exception as e:
                    logger.error(f"Загальна помилка при обробці авто: {e} (URL: {detail_url})")

            page += 1

        return all_parsed_cars_data_models

    @staticmethod
    def _parse_production_year(vehicle, ld_data):
        year_val = vehicle.get("productionYear")

        if not year_val:
            year_val = vehicle.get("firstRegistrationDateRaw")
        else:
            return year_val

        if not year_val:
            try:
                year_val = ld_data.get("offers", {}).get("itemOffered", {}).get("productionDate")
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
