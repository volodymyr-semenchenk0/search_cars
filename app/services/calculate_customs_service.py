from datetime import datetime
from typing import Optional, Dict

from app.utils.logger_config import logger
from .nbu_rate_service import NBURateService


class CalculateCustomsService:
    def __init__(self):
        self.living_minimum = 3028
        self.duty_rate = 0.10
        self.vat_rate = 0.20

    @staticmethod
    def _calculate_age_coefficients(production_year: int):
        current_year = datetime.now().year

        if not isinstance(production_year, int) or production_year <= 0 or production_year > current_year + 1:
            return None

        if production_year >= current_year:
            return 1
        elif production_year == current_year - 1:
            return 1
        else:
            # "кількість повних календарних років з року, наступного за роком виробництва"
            # Це (Рік розрахунку) - (Рік виробництва + 1)
            calculated_age = current_year - (production_year + 1)

            if calculated_age < 1:
                return 1
            elif calculated_age > 15:
                return 15
            else:
                return calculated_age

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
            return round(battery_capacity_kwh) * 1.0

        volume_l = engine_volume_cc / 1000

        if ft == "petrol":
            base = 50.0 if volume_l <= 3.0 else 100.0
        elif ft == "diesel":
            base = 75.0 if volume_l <= 3.5 else 150.0
        else:
            raise ValueError(f"Невідомий або необроблений тип палива для розрахунку акцизу ДВЗ: {fuel_type}")
        return base * volume_l * age_years

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

    def _calculate_pension_fee(self, price_uah: float) -> float:
        low = 165 * self.living_minimum
        med = 290 * self.living_minimum
        if price_uah <= low:
            rate = 0.03
        elif price_uah <= med:
            rate = 0.04
        else:
            rate = 0.05
        return price_uah * rate

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

        eur_to_uah_rate = NBURateService.get_eur_to_uah_rate()
        price_uah = round(price_eur * eur_to_uah_rate, 2)

        age_years = self._calculate_age_coefficients(production_year)
        fuel_type = _map_fuel_type(raw_fuel_type)

        excise_eur = self._calculate_excise(engine_volume_cc, age_years, fuel_type, battery_capacity_kwh)
        excise_uah = round(eur_to_uah_rate * excise_eur, 2)

        duty_uah = round(self._calculate_customs_duty(price_uah, fuel_type), 2)
        vat_uah = round(self._calculate_vat(price_uah, duty_uah, excise_uah, fuel_type), 2)
        pension_fee_uah = round(self._calculate_pension_fee(price_uah), 2)

        customs_payments_total_uah = round(duty_uah + excise_uah + vat_uah, 2)
        final_total_without_pension = round(customs_payments_total_uah + price_uah, 2)
        final_total = round(final_total_without_pension + pension_fee_uah, 2)

        return {
            "price_eur_input": price_eur,
            "price_uah": price_uah,
            "duty_uah": duty_uah,
            "excise_eur": excise_eur,
            "excise_uah": excise_uah,
            "vat_uah": vat_uah,
            "pension_fee_uah": pension_fee_uah,
            "customs_payments_total_uah": customs_payments_total_uah,
            "final_total_without_pension": final_total_without_pension,
            "final_total": final_total,
            "eur_to_uah_rate_actual": eur_to_uah_rate
        }


def _map_fuel_type(raw_fuel_type_input: str) -> str:
    if not raw_fuel_type_input or not isinstance(raw_fuel_type_input, str):
        raise ValueError(f"Некоректний або порожній тип пального: {raw_fuel_type_input}")

    s = raw_fuel_type_input.strip().lower()

    if s == "electric":
        return "electric"
    elif s == "electric/gasoline":
        return "petrol"
    elif s == "electric/diesel":
        return "diesel"
    elif s in ["gasoline", "lpg", "cng", "ethanol"]:
        return "petrol"
    elif s == "diesel":
        return "diesel"
    elif s == "hydrogen":
        logger.warning("Розрахунок для водневих авто потребує індивідуального підходу через специфіку законодавства.")
        raise ValueError(
            "Автоматичний розрахунок акцизу для водневих автомобілів наразі не підтримується.")

    elif s == "others":
        raise ValueError(
            f"Тип пального '{raw_fuel_type_input}' ('Інше') не дозволяє автоматично розрахувати акциз.")
    else:
        raise ValueError(f"Невідомий або непідтримуваний тип палива: '{raw_fuel_type_input}'")
