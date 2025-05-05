from flask import Flask, render_template, request, redirect, url_for, jsonify

from carquery_utils import get_all_makes, get_models_for_make
from database.db_manager import get_all_cars
from logger_config import logger
from parsers.autoscout24_parser import AutoScout24Parser
from utils import ENGINE_TYPES, COUNTRY_NAMES, COUNTRY_CODES

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    makes = get_all_makes()

    if request.method == "POST":
        data = request.form if request.method == "POST" else request.args

        brand = data.get("brand", "").strip().lower().replace(" ", "-") or None
        model = data.get("model", "").strip().lower().replace(" ", "-") or None
        fregto = data.get("fregto", "").strip() or None
        kmto = data.get("kmto", "").strip() or None
        cy = data.get("cy", "").strip() or None

        params = {
            "brand": brand,
            "model": model,
            "fregto": fregto,
            "kmto": kmto,
            "cy": cy
        }

        logger.debug(f"Параметри пошуку: {params}")

        parser = AutoScout24Parser(**params)
        parser.parse_autoscout24()
        return redirect(url_for("index"))

    # Виводимо збережені авто з БД
    columns = ["brand", "model", "year", "fuel_type", "engine_volume", "country", "price", "customs_uah",
               "final_price_uah", "link"]
    cars_raw = get_all_cars()
    cars = [dict(zip(columns, row)) for row in cars_raw]

    return render_template(
        "index.html",
        makes=makes,
        cars=cars,
        engine_types=ENGINE_TYPES,
        country_names=COUNTRY_NAMES,
        country_codes=COUNTRY_CODES
    )

@app.route("/api/models")
def api_models():
    make = request.args.get("make")
    if not make:
        return jsonify([])
    models = get_models_for_make(make)
    return jsonify(models)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
