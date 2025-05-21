from typing import Optional, Dict, Any, List

from app.repositories import CustomsCalculationRepository, OfferRepository, CarRepository
from app.utils.logger_config import logger
from .calculate_customs_service import CalculateCustomsService
from ..db import get_db_connection


class NotFoundError(Exception):
    pass


class ServiceError(Exception):
    pass


class OfferService:
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
                can_calculate = False
                if raw_fuel_type_from_data.lower() == "electric":
                    if battery_capacity_kwh is None:
                        logger.warning(
                            f"Для електрокара offer_id {offer_id} не вказано ємність батареї. Розрахунок мита неможливий.")
                    else:
                        can_calculate = True
                else:
                    if engine_volume_cc is None:
                        logger.warning(
                            f"Для авто offer_id {offer_id} з типом пального {raw_fuel_type_from_data} не вказано об'єм двигуна. Розрахунок мита неможливий.")
                    else:
                        can_calculate = True

                if can_calculate:
                    customs_calculator = CalculateCustomsService()
                    calc_results = customs_calculator.calculate(
                        price_eur,
                        engine_volume_cc,
                        production_year,
                        raw_fuel_type_from_data,
                        battery_capacity_kwh
                    )
                    if calc_results:
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
    def get_filtered_cars_list(
            make: Optional[str] = None,
            model: Optional[str] = None,
            fuel_type: Optional[str] = None,
            year: Optional[int] = None,
            country: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            make_id_int = int(make) if make and make.isdigit() else None
            model_id_int = int(model) if model and model.isdigit() else None
            year_int = int(year) if year and year.isdigit() else None

            return OfferRepository.get_filtered(
                make_id=make_id_int,
                model_id=model_id_int,
                fuel_type_key=fuel_type,
                year=year_int,
                country_of_listing=country,
                sort_by=sort
            )
        except Exception as e:
            logger.error(f"CarService: Помилка при отриманні списку пропозицій: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при отриманні списку пропозицій: {e}")

    @staticmethod
    def get_offer_details(offer_id: int) -> Dict[str, Any]:
        offer = OfferRepository.get_details_by_id(offer_id)
        if not offer:
            raise NotFoundError(f"Пропозиція з ID {offer_id} не знайдена.")
        return offer

    @staticmethod
    def remove_offer(offer_id: int) -> bool:
        try:
            if not OfferRepository.delete_cascade(offer_id):
                logger.warning(f"CarService: Не вдалося видалити пропозицію ID {offer_id}.")
                return False
            return True
        except Exception as e:
            logger.error(f"CarService: Помилка при видаленні пропозиції ID {offer_id}: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при видаленні пропозиції: {e}")

    @staticmethod
    def get_offers_list_by_ids(offer_ids: List[int]) -> List[Dict[str, Any]]:
        if not offer_ids:
            return []
        try:
            return OfferRepository.get_by_ids(offer_ids)
        except Exception as e:
            logger.error(f"CarService: Помилка отримання пропозицій для порівняння: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при отриманні пропозицій для порівняння: {e}")

    @staticmethod
    def update_offer_and_details(data: Dict[str, Any]) -> bool:
        offer_id = data.get('offer_id')
        if not offer_id:
            logger.error("OfferService: offer_id не надано для оновлення.")
            raise ServiceError("offer_id є обов'язковим для оновлення.")

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction()

            if 'price_eur' in data and data['price_eur'] is not None:
                OfferRepository.update_offer_price(offer_id, data['price_eur'], cursor)
                logger.info(f"OfferService: Оновлено ціну для offer_id {offer_id}.")

            car_id = data.get('car_id')
            powertrain_id = data.get('powertrain_id')

            if car_id:
                car_update_data = {}
                if 'production_year' in data and data['production_year'] is not None:
                    car_update_data['production_year'] = data['production_year']

                if car_update_data:
                    CarRepository.update_car_fields(car_id, car_update_data, cursor)
                    logger.info(f"OfferService: Оновлено дані в 'cars' для car_id {car_id} з {car_update_data}.")

                if powertrain_id:
                    powertrain_details_update_data = {
                        'engine_volume_cc': data.get('engine_volume_cc'),
                        'battery_capacity_kwh': data.get('battery_capacity_kwh'),
                        'raw_fuel_type': data.get('raw_fuel_type')
                    }

                    should_update_powertrain_details = False
                    if data.get('raw_fuel_type') == 'electric':
                        if data.get('battery_capacity_kwh') is not None or \
                                (data.get('battery_capacity_kwh') is None and 'battery_capacity_kwh' in data):
                            should_update_powertrain_details = True
                    else:
                        if data.get('engine_volume_cc') is not None or \
                                (data.get('engine_volume_cc') is None and 'engine_volume_cc' in data):
                            should_update_powertrain_details = True

                    if should_update_powertrain_details:
                        CarRepository.update_powertrain_details(powertrain_id, powertrain_details_update_data, cursor)
                        logger.info(f"OfferService: Оновлено деталі силової установки для powertrain_id {powertrain_id}.")


            price_for_calc = data.get("price_eur")
            year_for_calc = data.get("production_year")
            engine_for_calc = data.get("engine_volume_cc")
            battery_for_calc = data.get("battery_capacity_kwh")
            fuel_type_for_calc = data.get("raw_fuel_type")

            can_recalculate_customs = False
            if price_for_calc is not None and year_for_calc is not None and fuel_type_for_calc is not None:
                if fuel_type_for_calc.lower() == "electric":
                    if battery_for_calc is not None:
                        can_recalculate_customs = True
                else:
                    if engine_for_calc is not None:
                        can_recalculate_customs = True

            if can_recalculate_customs:
                logger.info(f"OfferService: Спроба перерахунку мита для offer_id {offer_id}.")
                customs_calculator = CalculateCustomsService()
                recalculated_customs_results = customs_calculator.calculate(
                    price_eur=price_for_calc,
                    engine_volume_cc=engine_for_calc,
                    production_year=year_for_calc,
                    raw_fuel_type=fuel_type_for_calc,
                    battery_capacity_kwh=battery_for_calc
                )
                if recalculated_customs_results:
                    if CustomsCalculationRepository.save_or_update(offer_id, recalculated_customs_results, db_cursor=cursor):
                        logger.info(f"OfferService: Митні розрахунки для offer_id {offer_id} успішно перераховано та збережено в рамках транзакції.")
                else:
                    logger.warning(f"OfferService: Перерахунок мита для offer_id {offer_id} не дав результатів. Існуючі розрахунки мита не змінено.")

            conn.commit()
            logger.info(f"OfferService: Транзакцію для оновлення offer_id {offer_id} успішно зафіксовано.")
            return True

        except Exception as e:
            if conn and conn.is_connected():
                conn.rollback()
                logger.error(f"OfferService: Транзакцію для offer_id {offer_id} відкочено через помилку: {e}", exc_info=True)
            raise ServiceError(f"Помилка сервісу при оновленні даних ({type(e).__name__}): {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()