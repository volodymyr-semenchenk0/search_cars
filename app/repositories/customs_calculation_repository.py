# app/repositories/customs_calculation_repository.py
from typing import Optional, Dict, Any

from app.db import execute_query, get_db_connection
from app.utils.logger_config import logger


class CustomsCalculationRepository:
    @staticmethod
    def get_by_offer_id(offer_id: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM customs_calculations WHERE offer_id = %s"
        try:
            rows = execute_query(sql, (offer_id,))
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Помилка отримання розрахунку мита для offer_id {offer_id}: {e}", exc_info=True)
            return None

    @staticmethod
    def save_or_update(offer_id: int, calc_results: Dict[str, Any]) -> bool:
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM customs_calculations WHERE offer_id = %s", (offer_id,))
            existing_calc = cursor.fetchone()

            if existing_calc:
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
                      WHERE offer_id = %s \
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
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                      """
                params = (
                    offer_id,
                    calc_results.get("duty_uah"), calc_results.get("excise_eur"), calc_results.get("excise_uah"),
                    calc_results.get("vat_uah"), calc_results.get("pension_fee_uah"),
                    calc_results.get("customs_payments_total_uah"), calc_results.get("final_total_without_pension"),
                    calc_results.get("final_total"), calc_results.get("eur_to_uah_rate_actual")
                )
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Помилка оновлення/створення розрахунків мита для offer_id {offer_id}: {e}", exc_info=True)
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
