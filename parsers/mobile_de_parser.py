import requests
from bs4 import BeautifulSoup
from database.db_manager import save_car_to_db

BASE_URL = "https://www.mobile.de/en"

def parse_mobile_de():
    search_url = BASE_URL + "/vehicles/car?isSearchRequest=true"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    car_elements = soup.find_all("div", class_="cBox-body")

    for car in car_elements:
        title_tag = car.find("span", class_="g-col-10")
        if not title_tag:
            continue  # пропускаємо блоки, які не є оголошеннями

        title = title_tag.text.strip()

        price_tag = car.find("span", class_="h3 u-text-bold")
        price = price_tag.text.strip() if price_tag else "N/A"

        link_tag = car.find("a", class_="link--muted no--text--decoration result-item")
        link = BASE_URL + link_tag["href"] if link_tag else "N/A"

        details = car.find_all("span", class_="g-col-6")
        if len(details) >= 2:
            year = details[0].text.strip()
            mileage = details[1].text.strip()
        else:
            year, mileage = "N/A", "N/A"

        if " " in title:
            brand, model = title.split(" ", 1)
        else:
            brand, model = title, ""

        car_data = (brand, model, year, price, mileage, link, "Mobile.de")
        save_car_to_db(car_data)

if __name__ == "__main__":
    parse_mobile_de()
