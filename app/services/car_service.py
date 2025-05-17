from typing import Optional, Dict, Any, List

from .calculate_customs_service import CalculateCustomsService
from app.repositories import CustomsCalculationRepository
from app.repositories import OfferRepository
from app.utils.logger_config import logger


class NotFoundError(Exception):
    pass


class ServiceError(Exception):
    pass


class CarService:
    @staticmethod
    def add_offer_from_parser(data: Dict[str, Any]) -> Optional[int]:
        try:
            offer_identifier = data.get("offer_identifier")
            source_id = data.get("source_id")

            if not offer_identifier or not source_id:
                logger.error("Не надано offer_identifier або source_id для додавання пропозиції.")
                raise ServiceError("Offer identifier and source ID are required.")

            if OfferRepository.exists(offer_identifier, source_id):
                logger.info(f"Пропозиція {offer_identifier} від source_id {source_id} вже існує. Пропуск.")
                return None

            offer_id = OfferRepository.create_full_offer_with_details(data)
            if offer_id is None:
                raise ServiceError(f"Не вдалося створити повну пропозицію для {offer_identifier}.")

            logger.info(f"CarService: Успішно додано пропозицію, повернуто offer_id: {offer_id}")

            price_eur = data.get("price")
            engine_volume_cc = data.get("engine_volume_cc")
            production_year = data.get("production_year")
            raw_fuel_type_from_data = data.get("raw_fuel_type")
            battery_capacity_kwh = data.get("battery_capacity_kwh")

            if price_eur is not None and production_year is not None and raw_fuel_type_from_data is not None:
                if raw_fuel_type_from_data.lower() == "electric" and battery_capacity_kwh is None:
                    logger.warning(
                        f"Для електрокара offer_id {offer_id} не вказано ємність батареї. Розрахунок мита неможливий.")
                elif raw_fuel_type_from_data.lower() != "electric" and engine_volume_cc is None:
                    logger.warning(
                        f"Для авто offer_id {offer_id} з типом пального {raw_fuel_type_from_data} не вказано об'єм двигуна. Розрахунок мита неможливий.")
                else:
                    customs_calculator = CalculateCustomsService()
                    calc_results = customs_calculator.calculate(
                        price_eur=price_eur,
                        engine_volume_cc=engine_volume_cc,
                        production_year=production_year,
                        raw_fuel_type=raw_fuel_type_from_data,
                        battery_capacity_kwh=battery_capacity_kwh
                    )
                    if calc_results:
                        # Використовуємо CustomsCalculationRepository
                        CustomsCalculationRepository.save_or_update(offer_id, calc_results)
                        logger.info(f"Розрахунки мита для offer_id {offer_id} збережено.")
                    else:
                        logger.warning(f"Не вдалося розрахувати мито для offer_id {offer_id}.")
            else:
                logger.warning(f"Недостатньо даних для розрахунку мита для offer_id {offer_id}.")
            return offer_id
        except ServiceError:
            raise
        except Exception as e:
            logger.error(f"CarService: Помилка при додаванні пропозиції {data.get('offer_identifier')}: {e}",
                         exc_info=True)
            raise ServiceError(f"Помилка сервісу при додаванні пропозиції: {e}")

    @staticmethod
    def list_cars(  # Назва методу може бути переглянута на list_offers_overview
            make_name: Optional[str] = None,
            model_name: Optional[str] = None,
            fuel_type: Optional[str] = None,
            year: Optional[int] = None,
            country_of_listing: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            # Використовуємо OfferRepository
            return OfferRepository.get_filtered(
                make_name=make_name,
                model_name=model_name,
                fuel_type_key=fuel_type,  # OfferRepository.get_filtered очікує fuel_type_key
                year=year,
                country_of_listing=country_of_listing,
                sort_by=sort
            )
        except Exception as e:
            logger.error(f"CarService: Помилка при отриманні списку пропозицій: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при отриманні списку пропозицій: {e}")

    @staticmethod
    def get_offer_details(offer_id: int) -> Dict[str, Any]:
        offer = OfferRepository.get_details_by_id(offer_id)  # Використовуємо OfferRepository
        if not offer:
            raise NotFoundError(f"Пропозиція з ID {offer_id} не знайдена.")
        return offer

    @staticmethod
    def remove_offer(offer_id: int) -> bool:
        try:
            if not OfferRepository.delete_cascade(offer_id):  # Використовуємо OfferRepository
                logger.warning(f"CarService: Не вдалося видалити пропозицію ID {offer_id}.")
                return False
            return True
        except Exception as e:
            logger.error(f"CarService: Помилка при видаленні пропозиції ID {offer_id}: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при видаленні пропозиції: {e}")

    @staticmethod
    def get_offers_for_comparison(offer_ids: List[int]) -> List[Dict[str, Any]]:
        if not offer_ids:
            return []
        try:
            return OfferRepository.get_by_ids(offer_ids)  # Використовуємо OfferRepository
        except Exception as e:
            logger.error(f"CarService: Помилка отримання пропозицій для порівняння: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при отриманні пропозицій для порівняння: {e}")

    @staticmethod
    def update_offer_customs_data(offer_id: int, data_to_update: Dict[str, Any]) -> bool:
        try:
            offer = OfferRepository.get_details_by_id(offer_id)  # Використовуємо OfferRepository
            if not offer:
                raise NotFoundError(f"Пропозиція з ID {offer_id} не знайдена для оновлення.")

            price_eur = data_to_update.get("price_eur", offer.get("price"))
            engine_volume_cc = data_to_update.get("engine_volume_cc")
            if engine_volume_cc is None and offer.get("engine_volume_cc") is not None:
                engine_volume_cc = offer.get("engine_volume_cc")

            production_year = data_to_update.get("production_year", offer.get("production_year"))
            raw_fuel_type_from_data = data_to_update.get("raw_fuel_type", offer.get("fuel_type"))
            battery_capacity_kwh = data_to_update.get("battery_capacity_kwh", offer.get("battery_capacity_kwh"))

            # TODO: Оновлення полів самої пропозиції (offers.price), авто (cars.*), силової установки (powertrains.*)
            # має відбуватися через відповідні репозиторії, якщо такі поля є в data_to_update.
            # Наприклад:
            # if "price_eur" in data_to_update and data_to_update["price_eur"] != offer.get("price"):
            #    OfferRepository.update_price(offer_id, data_to_update["price_eur"])
            # if "production_year" in data_to_update and data_to_update["production_year"] != offer.get("production_year"):
            #    CarRepository.update_car_field(offer.get("car_id"), "production_year", data_to_update["production_year"])

            if price_eur is not None and production_year is not None and raw_fuel_type_from_data is not None:
                # ... (логіка розрахунку мита залишається такою ж) ...
                customs_calculator = CalculateCustomsService()
                calc_results = customs_calculator.calculate(
                    price_eur=float(price_eur),
                    engine_volume_cc=float(engine_volume_cc) if engine_volume_cc is not None else None,
                    production_year=int(production_year),
                    raw_fuel_type=raw_fuel_type_from_data,
                    battery_capacity_kwh=float(battery_capacity_kwh) if battery_capacity_kwh is not None else None
                )
                if calc_results:
                    # Використовуємо CustomsCalculationRepository
                    if CustomsCalculationRepository.save_or_update(offer_id, calc_results):
                        logger.info(f"Розрахунки мита для offer_id {offer_id} оновлено/збережено.")
                        return True
                    else:
                        logger.error(f"Не вдалося зберегти оновлені розрахунки мита для offer_id {offer_id}.")
                        return False
                # ... (решта логіки) ...
                else:
                    logger.warning(f"Не вдалося перерахувати мито для offer_id {offer_id}.")
                    return False
            else:
                logger.warning(f"Недостатньо даних для перерахунку мита для offer_id {offer_id}.")
                return False
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"CarService: Помилка оновлення даних та мита для пропозиції {offer_id}: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при оновленні пропозиції {offer_id}: {e}")
