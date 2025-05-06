from flask import render_template, request, redirect, url_for, jsonify

from app.utils.carquery_utils import get_all_makes, get_models_for_make
from app.utils.utils import FUEL_TYPES, COUNTRY_NAMES, COUNTRY_CODES, PRICE_OPTIONS, MILEAGE_OPTIONS, get_years_list
from app.db import get_all_cars
from app.parsers.autoscout24_parser import AutoScout24Parser


def register_routes(app):
    @app.route("/", methods=["GET"])
    def index():
        makes = get_all_makes()

        columns = [
            'brand', 'model', 'year', 'fuel_type', 'engine_volume',
            'country', 'price', 'customs_uah', 'final_price_uah', 'link'
        ]
        cars = []
        for row in get_all_cars():
            car = dict(zip(columns, row))
            ev = car.get('engine_volume')
            if ev is not None:
                car['engine_liters'] = round(float(ev) / 1000, 1)
            else:
                car['engine_liters'] = None
            cars.append(car)

        return render_template(
            "index.html",
            makes=makes,
            cars=cars,
            years=get_years_list(),
            fuel_types=FUEL_TYPES,
            country_names=COUNTRY_NAMES,
            country_codes=COUNTRY_CODES,
            price_options=PRICE_OPTIONS,
            mileage_options=MILEAGE_OPTIONS
        )

    @app.route("/parse-query", methods=["GET"])
    def parse():
        data = request.form if request.method == "POST" else request.args

        params = {
            "brand": data.get("brand", "").strip().lower().replace(" ", "-") or None,
            "model": data.get("model", "").strip().lower().replace(" ", "-") or None,
            "pricefrom": data.get("pricefrom", "").strip() or None,
            "priceto": data.get("priceto", "").strip() or None,
            "fregfrom": data.get("fregfrom", "").strip() or None,
            "fregto": data.get("fregto", "").strip() or None,
            "kmfrom": data.get("kmfrom", "").strip() or None,
            "kmto": data.get("kmto", "").strip() or None,
            "cy": data.get("cy", "").strip() or None,
            "fuel": data.get("fuel", "").strip() or None
        }

        parser = AutoScout24Parser(**params)
        parser.parse_autoscout24()
        return redirect(url_for("index"))

    @app.route("/api/models")
    def api_models():
        make = request.args.get("make")
        if not make:
            return jsonify([])
        models = get_models_for_make(make)
        return jsonify(models)
