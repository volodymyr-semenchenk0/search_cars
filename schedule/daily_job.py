import schedule
import time
from parsers.autoscout24_parser import parse_autoscout24
from parsers.mobile_de_parser import parse_mobile_de

def run_parsers():
    print("Починаю щоденний парсинг...")
    parse_autoscout24()
    parse_mobile_de()
    print("Парсинг завершено!")

# Запускаємо парсери раз на добу
schedule.every().day.at("03:00").do(run_parsers)

if __name__ == "__main__":
    print("Система парсингу запущена. Очікування часу запуску...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Перевіряємо кожну хвилину
