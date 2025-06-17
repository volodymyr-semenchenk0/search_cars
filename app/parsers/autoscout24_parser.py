import json
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
import asyncio
import httpx

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
                 page_count: int = 5):
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

    async def _fetch_and_parse_offer(self, detail_url: str, client: httpx.AsyncClient) -> Optional[ParsedCarOffer]:
        try:
            details_resp = await client.get(detail_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            details_resp.raise_for_status()
            detail_soup = BeautifulSoup(details_resp.text, "lxml")

            short_data = detail_soup.find("script", type="application/ld+json")
            detailed_data = detail_soup.find("script", id="__NEXT_DATA__", type="application/json")
            if not detailed_data or not short_data:
                logger.warning(f"Required JSON data not found on {detail_url}")
                return None

            ld_data = json.loads(short_data.string)
            next_data = json.loads(detailed_data.string)
            listing = next_data["props"]["pageProps"]["listingDetails"]
            vehicle = listing.get("vehicle", {})

            fuel_formatted = vehicle.get("fuelCategory", {}).get("formatted")
            fuel_type_value = fuel_formatted.lower() if fuel_formatted else None

            car_data_dict = {
                "identifier": listing.get("id"),
                "link_to_offer": detail_url,
                "price": ld_data.get("offers", {}).get("price"),
                "currency": ld_data.get("offers", {}).get("priceCurrency"),
                "country_code": listing.get("location", {}).get("countryCode"),
                "make": vehicle.get("make"), "model": vehicle.get("model"),
                "year": self._parse_production_year(vehicle, ld_data),
                "body_type": vehicle.get("bodyType"),
                "fuel_type": fuel_type_value,
                "engine_volume": vehicle.get("rawDisplacementInCCM"),
                "battery_capacity_kwh": None, "transmission": vehicle.get("transmissionType"),
                "drive": vehicle.get("driveTrain"), "mileage": vehicle.get("mileageInKmRaw"),
            }

            if not self._is_listing_valid(car_data_dict):
                return None

            if car_data_dict["fuel_type"] == "electric":
                car_data_dict["battery_capacity_kwh"] = find_battery_capacity(
                    car_data_dict["make"], car_data_dict["model"], car_data_dict["year"]
                )

            validated_offer = ParsedCarOffer(**car_data_dict)
            logger.info(f"Successfully parsed and validated offer: {validated_offer.identifier}")
            return validated_offer
        except ValidationError as e:
            logger.error(f"Validation error for offer at URL {detail_url}: {e.errors()}")
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch offer details from {detail_url}: {e}")
        except Exception as e:
            logger.error(f"General error processing offer from {detail_url}: {e}", exc_info=True)
        return None

    async def _parse_async(self) -> list[ParsedCarOffer]:
        all_parsed_cars = []
        params, path = self._configure_url()
        async with httpx.AsyncClient() as client:
            for page in range(1, self.page_count + 1):
                params["page"] = str(page)
                query = "&".join([f"{k}={v}" for k, v in params.items()])
                url = self.base_url + path + "?" + query
                logger.info(f"Parsing page {page}: {url}")

                try:
                    response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    response.raise_for_status()
                except httpx.RequestError as e:
                    logger.error(f"Could not retrieve page {url}: {e}")
                    continue

                soup = BeautifulSoup(response.text, "lxml")
                car_elements = soup.find_all("article", class_="cldt-summary-full-item",
                                             attrs={"data-source": "listpage_search-results"})
                if not car_elements:
                    logger.info("No more listings or no results on page %s.", page)
                    break

                tasks = [
                    self._fetch_and_parse_offer(self.base_url + link["href"], client)
                    for car in car_elements
                    if (link := car.select_one('a[href^="/offers"]'))
                ]

                if tasks:
                    results = await asyncio.gather(*tasks)
                    all_parsed_cars.extend([res for res in results if res])
        return all_parsed_cars

    def parse(self) -> list[ParsedCarOffer]:
        return asyncio.run(self._parse_async())

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
