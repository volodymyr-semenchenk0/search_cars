# app/repositories/offer_repository.py
from typing import Optional, Dict, Any, List

from app.db import execute_query, get_db_connection
from app.repositories.car_repository import CarRepository
from app.utils.logger_config import logger


class OfferRepository:
    @staticmethod
    def exists(offer_identifier: str, source_id: int) -> bool:
        if not offer_identifier or not source_id:
            return False
        sql = "SELECT 1 FROM offers WHERE offer_identifier = %s AND source_id = %s LIMIT 1"
        try:
            rows = execute_query(sql, (offer_identifier, source_id))
            return bool(rows)
        except Exception as e:
            logger.error(f"Помилка перевірки існування оголошення {offer_identifier} для source_id {source_id}: {e}",
                         exc_info=True)
            raise

    @staticmethod
    def create_full_offer_with_details(data: Dict[str, Any]) -> Optional[int]:
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            conn.start_transaction()

            car_id = CarRepository.create_car_with_powertrain(data, cursor)
            if not car_id:
                conn.rollback()
                return None

            sql_offers = """
                         INSERT INTO offers (offer_identifier, car_id, source_id, link_to_offer,
                                             price, currency, country_of_listing)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)
                         """
            offer_params = (
                data.get("offer_identifier"),
                car_id,
                data.get("source_id"),
                data.get("link_to_offer"),
                data.get("price"),
                data.get("currency"),
                data.get("country_of_listing")
            )
            cursor.execute(sql_offers, offer_params)
            offer_id = cursor.lastrowid
            logger.info(f"Створено запис в 'offers' з ID: {offer_id} для car_id: {car_id}")

            conn.commit()
            logger.info(f"Успішно створено повну пропозицію з offer_id: {offer_id}")
            return offer_id

        except Exception as e:
            if conn and conn.is_connected():
                conn.rollback()
            logger.error(
                f"Помилка при створенні повної пропозиції (OfferRepository) для ідентифікатора {data.get('offer_identifier')}: {e}",
                exc_info=True)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_details_by_id(offer_id: int) -> Optional[Dict[str, Any]]:
        sql = """
              SELECT o.id             as offer_id,
                     o.link_to_offer,
                     o.price,
                     o.currency,
                     o.country_of_listing,
                     o.offer_identifier,
                     o.source_id,
                     o.offer_created_at     as offer_created_at,
                     s.name           as source_name,
                     s.url            as source_url,
                     c.id             as car_id,
                     c.production_year,
                     c.body_type,
                     c.transmission,
                     c.drive,
                     c.model_id,
                     cm.name          as model_name,
                     cma.name         as make_name,
                     pt.id            as powertrain_id,
                     pt.mileage,
                     pt.fuel_type_id,
                     ice.engine_volume_cc,
                     epd.battery_capacity_kwh,
                     ft.key_name      as fuel_type,
                     ft.label         as fuel_type_label,
                     cust.duty_uah,
                     cust.excise_uah,
                     cust.vat_uah,
                     cust.pension_fee_uah,
                     cust.customs_payments_total_uah,
                     cust.final_total as final_price_uah,
                     cust.eur_to_uah_rate_actual
              FROM offers o
                       JOIN cars c ON o.car_id = c.id
                       JOIN sources s ON o.source_id = s.id
                       LEFT JOIN car_models cm ON c.model_id = cm.id
                       LEFT JOIN car_makes cma ON cm.make_id = cma.id
                       LEFT JOIN powertrains pt ON pt.car_id = c.id
                       LEFT JOIN fuel_types ft ON pt.fuel_type_id = ft.id
                       LEFT JOIN ice_powertrain_details ice ON pt.id = ice.powertrain_id
                       LEFT JOIN electric_powertrain_details epd ON pt.id = epd.powertrain_id
                       LEFT JOIN customs_calculations cust ON cust.offer_id = o.id
              WHERE o.id = %s
              """
        try:
            rows = execute_query(sql, (offer_id,))
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Помилка отримання деталей пропозиції ID {offer_id} в OfferRepository: {e}", exc_info=True)
            return None

    @staticmethod
    def delete_cascade(offer_id: int) -> bool:
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction()

            cursor.execute("SELECT car_id FROM offers WHERE id = %s", (offer_id,))
            result = cursor.fetchone()

            if not result:
                logger.warning(f"Пропозиція з ID {offer_id} не знайдена для видалення.")
                conn.rollback()
                return False

            car_id_to_delete = result.get('car_id')

            if not car_id_to_delete:
                logger.error(f"Для пропозиції ID {offer_id} не знайдено пов'язаного car_id, хоча пропозиція існує. Видалення неможливе без car_id.")
                conn.rollback()
                return False

            cursor.execute("DELETE FROM offers WHERE id = %s", (offer_id,))
            offers_deleted_count = cursor.rowcount
            logger.info(f"Видалено {offers_deleted_count} записів з 'offers' для offer_id {offer_id}.")

            if offers_deleted_count > 0:
                cursor.execute("SELECT COUNT(*) as count FROM offers WHERE car_id = %s", (car_id_to_delete,))
                other_offers_count_result = cursor.fetchone()
                other_offers_count = other_offers_count_result.get('count', 0) if other_offers_count_result else 0

                if other_offers_count == 0:
                    logger.info(
                        f"Немає інших пропозицій для car_id {car_id_to_delete}. Видалення авто та пов'язаних даних.")
                    car_deleted = CarRepository.delete_car_and_dependencies(car_id_to_delete, cursor)
                    if not car_deleted:
                        logger.error(f"Не вдалося видалити автомобіль car_id {car_id_to_delete}, хоча він мав бути видалений.")
                else:
                    logger.info(
                        f"Існують інші пропозиції ({other_offers_count}) для car_id {car_id_to_delete}. Авто не видаляється.")

            conn.commit()
            return offers_deleted_count > 0

        except Exception as e:
            if conn and conn.is_connected():
                conn.rollback()
            logger.error(f"Помилка при видаленні пропозиції ID {offer_id} (OfferRepository): {e}", exc_info=True)
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_filtered(
            make_id: Optional[int] = None,
            model_id: Optional[int] = None,
            fuel_type_key: Optional[str] = None,
            year: Optional[int] = None,
            country_of_listing: Optional[str] = None,
            sort_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        base_sql = """
                   SELECT o.id             as offer_id,
                          o.link_to_offer,
                          o.price,
                          o.currency,
                          o.country_of_listing,
                          o.offer_identifier,
                          o.source_id,
                          o.offer_created_at,
                          s.name           as source_name,
                          s.url            as source_url,
                          c.id             as car_id,
                          c.production_year,
                          c.body_type,
                          c.transmission,
                          c.drive,
                          cm.id            as car_model_id,
                          cm.name          as model_name,
                          cma.id           as car_make_id,
                          cma.name         as make_name,
                          pt.id            as powertrain_id,
                          pt.mileage,
                          pt.fuel_type_id,
                          ice.engine_volume_cc,
                          epd.battery_capacity_kwh,
                          ft.key_name      as fuel_type,
                          ft.label         as fuel_type_label,
                          cust.duty_uah,
                          cust.excise_uah,
                          cust.vat_uah,
                          cust.pension_fee_uah,
                          cust.customs_payments_total_uah,
                          cust.final_total as final_price_uah,
                          cust.eur_to_uah_rate_actual
                   FROM offers o
                            JOIN cars c ON o.car_id = c.id
                            JOIN sources s ON o.source_id = s.id
                            LEFT JOIN car_models cm ON c.model_id = cm.id
                            LEFT JOIN car_makes cma ON cm.make_id = cma.id
                            LEFT JOIN powertrains pt ON pt.car_id = c.id
                            LEFT JOIN fuel_types ft ON pt.fuel_type_id = ft.id
                            LEFT JOIN ice_powertrain_details ice ON pt.id = ice.powertrain_id
                            LEFT JOIN electric_powertrain_details epd ON pt.id = epd.powertrain_id
                            LEFT JOIN customs_calculations cust ON cust.offer_id = o.id
                   """
        where_clauses = []
        params = []

        if make_id is not None:
            where_clauses.append("cma.id = %s")
            params.append(make_id)
        if model_id is not None:
            where_clauses.append("cm.id = %s")
            params.append(model_id)
        if fuel_type_key:
            where_clauses.append("ft.key_name = %s")
            params.append(fuel_type_key)
        if year is not None:
            where_clauses.append("c.production_year = %s")
            params.append(year)
        if country_of_listing:
            where_clauses.append("o.country_of_listing = %s")
            params.append(country_of_listing)

        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        if sort_by == 'price_asc':
            base_sql += " ORDER BY o.price ASC, o.id DESC"
        elif sort_by == 'price_desc':
            base_sql += " ORDER BY o.price DESC, o.id DESC"
        elif sort_by == 'oldest':
            base_sql += " ORDER BY o.offer_created_at ASC, o.id ASC"
        else:
            base_sql += " ORDER BY o.offer_created_at DESC, o.id DESC"

        try:
            return execute_query(base_sql, tuple(params))
        except Exception as e:
            logger.error(f"Помилка отримання відфільтрованих пропозицій: {e}", exc_info=True)
            return []

    @staticmethod
    def get_by_ids(offer_ids: List[int]) -> List[Dict[str, Any]]:
        if not offer_ids:
            return []

        placeholders = ','.join(['%s'] * len(offer_ids))
        sql = f"""
            SELECT
                o.id as offer_id, o.link_to_offer, o.price, o.currency, o.country_of_listing,
                s.name as source_name,
                c.production_year, c.body_type, c.transmission, c.drive,
                cm.name as model_name,
                cma.name as make_name,
                pt.mileage,
                ice.engine_volume_cc,
                epd.battery_capacity_kwh,
                ft.key_name as fuel_type, ft.label as fuel_type_label,
                cust.customs_payments_total_uah,
                cust.final_total as final_price_uah,
                cust.eur_to_uah_rate_actual
            FROM offers o
            JOIN cars c ON o.car_id = c.id
            JOIN sources s ON o.source_id = s.id
            LEFT JOIN car_models cm ON c.model_id = cm.id
            LEFT JOIN car_makes cma ON cm.make_id = cma.id
            LEFT JOIN powertrains pt ON pt.car_id = c.id
            LEFT JOIN fuel_types ft ON pt.fuel_type_id = ft.id
            LEFT JOIN ice_powertrain_details ice ON pt.id = ice.powertrain_id
            LEFT JOIN electric_powertrain_details epd ON pt.id = epd.powertrain_id
            LEFT JOIN customs_calculations cust ON cust.offer_id = o.id
            WHERE o.id IN ({placeholders})
            ORDER BY FIELD(o.id, {placeholders}) 
        """
        params = tuple(offer_ids) * 2 if len(offer_ids) > 0 else tuple()

        try:
            return execute_query(sql, params)
        except Exception as e:
            logger.error(f"Помилка отримання пропозицій за списком ID (OfferRepository): {e}", exc_info=True)
            return []

    @staticmethod
    def update_offer_price(offer_id: int, price: float, cursor: Any) -> bool:
        sql = "UPDATE offers SET price = %s WHERE id = %s"
        try:
            cursor.execute(sql, (price, offer_id))
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Помилка оновлення ціни для offer_id {offer_id}: {e}", exc_info=True)
            raise