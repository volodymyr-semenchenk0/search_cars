from flask import Flask, render_template, request, redirect, url_for
from parsers.autoscout24_parser import parse_autoscout24
from database.db_manager import get_all_cars
from utils import ENGINE_TYPES, COUNTRY_NAMES, COUNTRY_CODES

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    columns = ["brand", "model", "year", "fuel_type", "engine_volume", "country", "price", "customs_uah", "final_price_uah", "link"]
    cars_raw = get_all_cars()
    cars = [dict(zip(columns, row)) for row in cars_raw]
    return render_template(
        "index.html",
        cars=cars,
        engine_types=ENGINE_TYPES,
        country_codes=COUNTRY_CODES,
        country_names=COUNTRY_NAMES
    )

@app.route("/search", methods=["POST"])
def search():
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()
    fregto = request.form.get("fregto", "").strip()
    kmto = request.form.get("kmto", "").strip()
    cy = request.form.get("cy", "").strip()

    # Побудова параметрів
    params = {
        "brand": brand or None,
        "model": model or None,
        "fregto": fregto or None,
        "kmto": kmto or None,
        "cy": cy or None
    }

    print(params)
    parse_autoscout24(**params)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)