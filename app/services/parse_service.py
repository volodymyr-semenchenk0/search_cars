from app.parsers import ParserFactory
from app.repositories import FuelTypeRepository, CarMakeRepository, CarModelRepository, OfferRepository
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

        try:
            existing_identifiers = OfferRepository.get_existing_identifiers_for_source(source_id)
        except Exception as e:
            logger.error(f"Не вдалося отримати існуючі ідентифікатори. Помилка: {e}", exc_info=True)
            return 0, []

        processed_in_this_batch = set()
        new_parsed_offers = []
        for offer in parsed_offers:
            if offer.identifier not in existing_identifiers and offer.identifier not in processed_in_this_batch:
                new_parsed_offers.append(offer)
                processed_in_this_batch.add(offer.identifier)

        if not new_parsed_offers:
            logger.info("Всі знайдені пропозиції вже існують в базі даних або є дублікатами.")
            return 0, []

        logger.info(f"Знайдено {len(new_parsed_offers)} унікальних нових пропозицій для збереження.")

        offers_to_create = []
        for offer_dto in new_parsed_offers:
            try:
                make_id = CarMakeRepository.get_or_create_id(offer_dto.make) if offer_dto.make else None
                model_id = CarModelRepository.get_or_create_id(make_id,
                                                               offer_dto.model) if make_id and offer_dto.model else None

                if not model_id:
                    logger.warning(
                        f"ParseService: Не вдалося визначити model_id для пропозиції "
                        f"'{offer_dto.identifier}' (make: '{offer_dto.make}', model: '{offer_dto.model}'). Пропуск.")
                    continue

                fuel_type_id = FuelTypeRepository.get_id_by_key_name(
                    offer_dto.fuel_type) if offer_dto.fuel_type else None

                data_for_service = {
                    "offer_identifier": offer_dto.identifier,
                    "source_id": source_id,
                    "link_to_offer": offer_dto.link_to_offer,
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
                offers_to_create.append(data_for_service)
            except Exception as e:
                logger.error(f"ParseService: Помилка підготовки даних для пропозиції {offer_dto.identifier}: {e}",
                             exc_info=True)

        if not offers_to_create:
            logger.warning("Не залишилось пропозицій для створення після підготовки даних.")
            return 0, []

        try:
            newly_saved_offer_ids = OfferService.bulk_add_offers_from_parser(offers_to_create)
            saved_cars_count = len(newly_saved_offer_ids)
            logger.info(f"ParseService: Успішно передано на масове збереження {saved_cars_count} пропозицій.")
            return saved_cars_count, newly_saved_offer_ids
        except OfferServiceError as e:
            logger.error(f"ParseService: Помилка від OfferService при масовій обробці: {e}")
            return 0, []
        except Exception as e:
            logger.error(f"ParseService: Непередбачена помилка при масовій обробці пропозицій: {e}", exc_info=True)
            return 0, []
