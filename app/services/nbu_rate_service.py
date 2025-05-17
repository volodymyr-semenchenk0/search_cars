import time
from datetime import datetime
from typing import Optional

import requests

from app.utils.logger_config import logger

_cached_rates = {}
CACHE_DURATION_SECONDS = 86400

DEFAULT_RATE_ON_API_FAILURE = 46.2852


class NBURateService:
    @staticmethod
    def get_eur_to_uah_rate(calculation_date: Optional[datetime] = None) -> float:
        global _cached_rates

        date_str = calculation_date.strftime('%Y%m%d') if calculation_date else datetime.now().strftime('%Y%m%d')

        current_time = time.time()

        if date_str in _cached_rates:
            rate, timestamp = _cached_rates[date_str]
            if (current_time - timestamp) < CACHE_DURATION_SECONDS:
                logger.info(f"Повертаю кешований курс євро для {date_str}: {rate}")
                return rate

        logger.info(f"Оновлюю курс євро з API НБУ для дати: {date_str}")
        try:
            response = requests.get(
                f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&date={date_str}&json",
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            if data and isinstance(data, list) and data[0] and "rate" in data[0]:
                rate = float(data[0]["rate"])
                _cached_rates[date_str] = (rate, current_time)  # Кешуємо з часовою міткою
                logger.info(f"Курс євро для {date_str} успішно оновлено: {rate}")
                return rate
            else:
                logger.warning(f"Не вдалося отримати коректні дані курсу євро від НБУ для {date_str}.")
        except requests.RequestException as e:
            logger.error(f"Помилка при запиті курсу євро для {date_str} (RequestException): {e}")
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Помилка обробки даних курсу євро для {date_str}: {e}")
        except Exception as e:
            logger.error(f"Непередбачена помилка при отриманні курсу євро для {date_str}: {e}")

        if date_str in _cached_rates:
            rate, _ = _cached_rates[date_str]
            logger.warning(f"Повертаю старий кешований курс для {date_str}: {rate} через помилку оновлення.")
            return rate

        logger.warning(f"Повертаю дефолтний курс через помилку API для {date_str}: {DEFAULT_RATE_ON_API_FAILURE}")
        return DEFAULT_RATE_ON_API_FAILURE
