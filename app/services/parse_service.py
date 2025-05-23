from app.parsers import ParserFactory
from app.repositories import FuelTypeRepository, CarMakeRepository, CarModelRepository
from app.schemas.parsed_offer import ParsedCarOffer
from app.utils.logger_config import logger
from .offer_service import OfferService, ServiceError as OfferServiceError
from .source_service import SourceService


class ParseService:
    @staticmethod
    def parse_website(source_id: int, **filters) -> tuple[int, list[int]]:
        src = SourceService.get_source_by_id(source_id)

        parsed_offers: list[ParsedCarOffer] = ParserFactory.get(
            name=src['name'],
            base_url=src['url'],
            **filters
        ).parse()

        if not parsed_offers:
            logger.info(f"Парсер для {src['name']} не повернув жодних пропозицій за фільтрами.")
            return 0, []

        saved_cars_count = 0
        processed_offers_count = 0
        newly_saved_offer_ids = []

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
                if offer_dto.model and not model_id and make_id:
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
                    "raw_fuel_type": offer_dto.fuel_type
                }

                created_offer_id = OfferService.add_offer_from_parser(data_for_service)
                if created_offer_id:
                    logger.info(
                        f"ParseService: Успішно оброблено та передано на збереження пропозицію {offer_dto.identifier}, new offer_id: {created_offer_id}.")
                    saved_cars_count += 1
                    newly_saved_offer_ids.append(created_offer_id)
                else:
                    logger.info(
                        f"ParseService: Пропозиція {offer_dto.identifier} вже існує або не була збережена сервісом (повернуто None).")

            except OfferServiceError as e:
                logger.error(f"ParseService: Помилка від OfferService при обробці {offer_dto.identifier}: {e}")
            except Exception as e:
                logger.error(f"ParseService: Непередбачена помилка при обробці пропозиції {offer_dto.identifier}: {e}",
                             exc_info=True)

        return saved_cars_count, newly_saved_offer_ids
