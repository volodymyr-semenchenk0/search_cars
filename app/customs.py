from datetime import datetime
from typing import Optional, Dict

import requests

from app.utils.logger_config import logger


class CalculateCustoms:
    @staticmethod
    def get_eur_to_uah_rate() -> float:
        try:
            response = requests.get(
                "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&json"
            )
            if response.status_code == 200:
                data = response.json()
                return float(data[0]["rate"])
            else:
                logger.warning(f"Не вдалося отримати курс євро від НБУ. Статус: {response.status_code}")
        except Exception as e:
            logger.warning(f"Помилка при запиті курсу євро: {e}")
        return 47.0

    @staticmethod
    def _map_fuel_type(raw: str) -> str:

        s = raw.strip().lower()

        if 'hybrid' in s or 'electric/gasoline' in s or 'electric/diesel' in s:
            return 'hybrid'

        if 'electric' in s:
            return 'electric'

        if any(fuel in s for fuel in ['gasoline', 'petrol', 'lpg', 'cng', 'ethanol', 'hydrogen']):
            return 'petrol'

        if 'diesel' in s:
            return 'diesel'

        raise ValueError(f"Тип палива '{raw}' не підтримується")

    def __init__(self):
        self.eur_to_uah_rate = self.get_eur_to_uah_rate()
        self.living_minimum = 3028
        self.duty_rate = 0.10
        self.vat_rate = 0.20

    def _calculate_customs_duty(self, customs_value_uah: float, fuel_type: str) -> float:
        if fuel_type.lower() == "electric":
            return 0.0
        return customs_value_uah * self.duty_rate

    @staticmethod
    def _calculate_excise(
            engine_volume_cc: float,
            age_years: int,
            fuel_type: str,
            battery_capacity_kwh: Optional[float] = None
    ) -> float:
        ft = fuel_type

        if ft == "electric":
            if battery_capacity_kwh is None:
                raise ValueError("Потрібно вказати battery_capacity_kwh для електрокара")
            return battery_capacity_kwh * 1.0

        volume_l = engine_volume_cc / 1000
        age = age_years

        if ft == "hybrid":
            base = 100.0
        elif ft == "petrol":
            base = 50.0 if volume_l <= 3 else 100.0
        elif ft == "diesel":
            base = 75.0 if volume_l <= 3.5 else 150.0
        else:
            raise ValueError(f"Невідомий тип палива: {fuel_type}")
        return base * volume_l * age

    def _calculate_vat(
            self,
            customs_value_uah: float,
            duty_uah: float,
            excise_uah: float,
            fuel_type: str
    ) -> float:
        if fuel_type.lower() == "electric":
            return 0.0
        return (customs_value_uah + duty_uah + excise_uah) * self.vat_rate

    def _calculate_pension_fee(self, customs_value_uah: float) -> float:
        low = 165 * self.living_minimum
        med = 290 * self.living_minimum
        if customs_value_uah <= low:
            rate = 0.03
        elif customs_value_uah <= med:
            rate = 0.04
        else:
            rate = 0.05
        return customs_value_uah * rate

    def calculate(
            self,
            price_eur: float,
            engine_volume_cc: float,
            production_year: int,
            raw_fuel_type: str,
            battery_capacity_kwh: Optional[float] = None
    ) -> Optional[Dict[str, float]]:

        if price_eur is None or production_year is None:
            return None
        if raw_fuel_type == 'electric':
            if battery_capacity_kwh is None:
                return None
        else:
            if engine_volume_cc is None:
                return None

        price_uah = price_eur * self.eur_to_uah_rate
        current_year = datetime.now().year
        age_years = max(1, min(current_year - production_year, 15))
        fuel_type = self._map_fuel_type(raw_fuel_type)

        excise_eur = CalculateCustoms._calculate_excise(
            engine_volume_cc, age_years, fuel_type, battery_capacity_kwh
        )
        excise_uah = excise_eur * self.eur_to_uah_rate
        duty = self._calculate_customs_duty(price_uah, fuel_type)
        vat = self._calculate_vat(price_uah, duty, excise_uah, fuel_type)
        pension = self._calculate_pension_fee(price_uah)
        total_without_pension = price_uah + duty + excise_uah + vat
        total = total_without_pension + pension

        return {
            "price_uah": round(price_uah, 2),
            "duty": round(duty, 2),
            "excise_eur": round(excise_eur, 2),
            "excise_uah": round(excise_uah, 2),
            "vat": round(vat, 2),
            "pension_fee": round(pension, 2),
            "total_without_pension": round(total_without_pension, 2),
            "total": round(total, 2)
        }
