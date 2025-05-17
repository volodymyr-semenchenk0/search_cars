from flask import flash
from app.parsers import ParserFactory
from .source_service import SourceService
from .car_service import CarService, ServiceError as CarServiceError
from app.repositories import FuelTypeRepository
from app.repositories import CarMakeRepository
from app.repositories import CarModelRepository
from app.schemas.parsed_offer import ParsedCarOffer
from app.utils.logger_config import logger


class ParseService:
    @staticmethod
    def parse_website(source_id: int, **filters) -> int:
        src = SourceService.get_source_by_id(source_id)

        parsed_offers: list[ParsedCarOffer] = ParserFactory.get(
            name=src['name'],
            base_url=src['url'],
            **filters
        ).parse()

        if not parsed_offers:
            logger.info(f"Парсер для {src['name']} не повернув жодних пропозицій за фільтрами.")
            flash(f"За вашим запитом на {src['name']} нічого не знайдено.", 'info')
            return 0

        saved_cars_count = 0
        processed_offers_count = 0

        for offer_dto in parsed_offers:
            processed_offers_count += 1
            try:
                make_id = None
                if offer_dto.make:
                    make_id = CarMakeRepository.get_or_create_id(offer_dto.make)

                model_id = None
                if make_id and offer_dto.model:
                    model_id = CarModelRepository.get_or_create_id(make_id, offer_dto.model)

                fuel_type_id = None
                if offer_dto.fuel_type:
                    fuel_type_id = FuelTypeRepository.get_id_by_key_name(offer_dto.fuel_type)

                if offer_dto.make and not make_id:
                    logger.warning(
                        f"ParseService: Не вдалося отримати/створити make_id для '{offer_dto.make}'. Пропуск: {offer_dto.identifier}")
                    continue
                if offer_dto.model and not model_id:
                    logger.warning(
                        f"ParseService: Не вдалося отримати/створити model_id для '{offer_dto.model}' (make_id: {make_id}). Пропуск: {offer_dto.identifier}")
                    continue

                data_for_service = {
                    "offer_identifier": offer_dto.identifier,
                    "source_id": source_id,
                    "link_to_offer": str(offer_dto.link_to_offer),
                    "price": offer_dto.price,
                    "currency": offer_dto.currency,
                    "country_of_listing": offer_dto.country_code,
                    "model_id": model_id,
                    "production_year": offer_dto.year,
                    "body_type_str": offer_dto.body_type,
                    "transmission_str": offer_dto.transmission,
                    "drive_str": offer_dto.drive,
                    "fuel_type_id": fuel_type_id,
                    "engine_volume_cc": offer_dto.engine_volume,
                    "battery_capacity_kwh": offer_dto.battery_capacity_kwh,
                    "mileage_km": offer_dto.mileage,
                    "raw_fuel_type": offer_dto.fuel_type  # Передаємо ключ типу пального
                }

                created_offer_id = CarService.add_offer_from_parser(data_for_service)
                if created_offer_id:
                    logger.info(
                        f"ParseService: Успішно оброблено та передано на збереження пропозицію {offer_dto.identifier}, new offer_id: {created_offer_id}.")
                    saved_cars_count += 1
                else:
                    logger.info(
                        f"ParseService: Пропозиція {offer_dto.identifier} вже існує або не була збережена сервісом (повернуто None).")

            except CarServiceError as e:
                logger.error(f"ParseService: Помилка від CarService при обробці {offer_dto.identifier}: {e}")
            except Exception as e:
                logger.error(f"ParseService: Непередбачена помилка при обробці пропозиції {offer_dto.identifier}: {e}",
                             exc_info=True)

        if saved_cars_count > 0:
            flash(
                f"Успішно збережено {saved_cars_count} нових авто з {processed_offers_count} знайдених на {src['name']}.",
                'success')
        elif parsed_offers:
            flash(
                f"Знайдено {processed_offers_count} авто на {src['name']}, але нових для збереження не було (вже існують або не вдалося обробити).",
                'info')

        return saved_cars_count
