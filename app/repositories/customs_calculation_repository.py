from typing import Optional, Dict, Any

import mysql.connector

from app.db import get_db_connection
from app.utils.logger_config import logger


class CustomsCalculationRepository:
    @staticmethod
    def get_by_offer_id(offer_id: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM customs_calculations WHERE offer_id = %s"
        try:
            from app.db import execute_query
            rows = execute_query(sql, (offer_id,))
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Помилка отримання розрахунку мита для offer_id {offer_id}: {e}", exc_info=True)
            return None

    @staticmethod
    def save_or_update(offer_id: int, calc_results: Dict[str, Any], db_cursor: Optional[Any] = None) -> bool:

        conn_managed_locally = False
        conn = None

        cursor = db_cursor

        try:
            if not cursor:
                conn = get_db_connection()
                cursor = conn.cursor()
                conn_managed_locally = True

            select_sql = "SELECT id FROM customs_calculations WHERE offer_id = %s"
            cursor.execute(select_sql, (offer_id,))
            existing_calc_row = cursor.fetchone()

            if existing_calc_row:
                sql = """
                      UPDATE customs_calculations
                      SET duty_uah                    = %s,
                          excise_eur                  = %s,
                          excise_uah                  = %s,
                          vat_uah                     = %s,
                          pension_fee_uah             = %s,
                          customs_payments_total_uah  = %s,
                          final_total_without_pension = %s,
                          final_total                 = %s,
                          eur_to_uah_rate_actual      = %s,
                          updated_at                  = CURRENT_TIMESTAMP
                      WHERE offer_id = %s
                      """
                params = (
                    calc_results.get("duty_uah"), calc_results.get("excise_eur"), calc_results.get("excise_uah"),
                    calc_results.get("vat_uah"), calc_results.get("pension_fee_uah"),
                    calc_results.get("customs_payments_total_uah"), calc_results.get("final_total_without_pension"),
                    calc_results.get("final_total"), calc_results.get("eur_to_uah_rate_actual"),
                    offer_id
                )
            else:
                sql = """
                      INSERT INTO customs_calculations
                      (offer_id, duty_uah, excise_eur, excise_uah, vat_uah, pension_fee_uah,
                       customs_payments_total_uah, final_total_without_pension, final_total, eur_to_uah_rate_actual)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      """
                params = (
                    offer_id,
                    calc_results.get("duty_uah"), calc_results.get("excise_eur"), calc_results.get("excise_uah"),
                    calc_results.get("vat_uah"), calc_results.get("pension_fee_uah"),
                    calc_results.get("customs_payments_total_uah"), calc_results.get("final_total_without_pension"),
                    calc_results.get("final_total"), calc_results.get("eur_to_uah_rate_actual")
                )

            cursor.execute(sql, params)

            if conn_managed_locally and conn:
                conn.commit()

            return cursor.rowcount > 0

        except mysql.connector.Error as db_err:
            if conn_managed_locally and conn and conn.is_connected():
                conn.rollback()
            logger.error(
                f"Помилка бази даних при оновленні/створенні розрахунків мита для offer_id {offer_id}: {db_err}",
                exc_info=True)
            if db_cursor:
                raise
            return False
        except Exception as e:
            if conn_managed_locally and conn and conn.is_connected():
                conn.rollback()
            logger.error(f"Загальна помилка при оновленні/створенні розрахунків мита для offer_id {offer_id}: {e}",
                         exc_info=True)
            if db_cursor:
                raise
            return False
        finally:
            if conn_managed_locally:
                if cursor and not db_cursor:
                    cursor.close()
                if conn:
                    conn.close()
