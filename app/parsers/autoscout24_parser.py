import json
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from pydantic_core._pydantic_core import ValidationError

from app.schemas.parsed_offer import ParsedCarOffer
from app.utils.ev_utils import find_battery_capacity
from app.utils.logger_config import logger


class AutoScout24Parser:
    _searched_cars_count = 0

    def __init__(self, base_url: str,
                 make: Optional[str] = None, model: Optional[str] = None,
                 pricefrom: Optional[int] = None, priceto: Optional[int] = None,
                 fregfrom: Optional[int] = None, fregto: Optional[int] = None,
                 kmfrom: Optional[int] = None, kmto: Optional[int] = None,
                 cy: Optional[str] = None, fuel: Optional[str] = None,
                 page_count: int = 2):
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

    def _configure_url(self) -> Tuple[Dict[str, Any], str]:

        params: Dict[str, Any] = {
            "sort": "standard",
            "desc": "0",
            "ustate": "N,U",
            "size": "20",
            "atype": "C",
            "damaged_listing": "exclude",
        }

        param_mapping = {
            'fregfrom': 'fregfrom',
            'fregto': 'fregto',
            'pricefrom': 'pricefrom',
            'priceto': 'priceto',
            'kmfrom': 'kmfrom',
            'kmto': 'kmto',
            'cy': 'cy',
            'fuel': 'fuel',
        }

        for attr_name, param_key in param_mapping.items():
            value = getattr(self, attr_name, None)
            if value is not None:

                if isinstance(value, str) and not value.strip():
                    continue
                params[param_key] = value

        path_segments = ["/lst"]

        if self.make:
            path_segments.append(self.make)
        if self.model:

            if self.make:
                path_segments.append(self.model)

        path = "/".join(path_segments)

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

                    if not self._is_listing_valid(car_data_dict):
                        return []

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

    def _is_listing_valid(self, parsed_data: Dict[str, Any]) -> bool:

        if self.make:
            parsed_make = (parsed_data.get('make') or '').strip().lower().replace(' ', '-')
            if self.make != parsed_make:
                logger.warning(
                    f"Невідповідність марки: фільтр '{self.make}', отримано '{parsed_make}' "
                    f"для ID {parsed_data.get('identifier')}"
                )
                return False

        if self.model:
            parsed_model = (parsed_data.get('model') or '').strip().lower().replace(' ', '-')
            if self.model != parsed_model:
                logger.warning(
                    f"Невідповідність моделі: фільтр '{self.model}', отримано '{parsed_model}' "
                    f"для ID {parsed_data.get('identifier')}"
                )
                return False

        return True

