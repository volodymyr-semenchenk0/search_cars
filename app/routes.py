from flask import render_template, request, redirect, url_for, jsonify

from app.data.options import FUEL_TYPES, COUNTRY_NAMES, COUNTRY_CODES, PRICE_OPTIONS, MILEAGE_OPTIONS, get_years_list
from app.parsers.autoscout24_parser import AutoScout24Parser
from app.services.car_service import get_filtered_cars
from app.utils.carquery_utils import get_all_makes, get_models_for_make

makes = get_all_makes()


def register_routes(app):
    @app.route("/", methods=["GET"])
    def index():
        raw_args = request.args.to_dict()
        clean_args = {k: v for k, v in raw_args.items() if v}
        if raw_args and raw_args != clean_args:
            return redirect(url_for('index', **clean_args))

        fields = ("make", "model", "fuel", "year", "country", "sort")
        selected = {f: request.args.get(f) for f in fields}

        cars = get_filtered_cars(**selected)

        for car in cars:
            ev = car.get('engine_volume')
            car['engine_liters'] = round(float(ev) / 1000, 1) if ev else None

        return render_template(
            'main.html',
            cars=cars,
            makes=makes,
            years=get_years_list(),
            fuel_types=FUEL_TYPES,
            country_names=COUNTRY_NAMES,
            price_options=PRICE_OPTIONS,
            mileage_options=MILEAGE_OPTIONS,
            selected=selected
        )

    @app.route("/search", methods=["GET"])
    def search():
        selected = request.args.to_dict()
        return render_template(
            "search.html",
            makes=makes,
            years=get_years_list(),
            fuel_types=FUEL_TYPES,
            country_names=COUNTRY_NAMES,
            country_codes=COUNTRY_CODES,
            price_options=PRICE_OPTIONS,
            mileage_options=MILEAGE_OPTIONS,
            selected=selected
        )

    @app.route("/search/parse-query", methods=["POST"])
    def parse_query():
        data = request.form if request.method == "POST" else request.args

        params = {
            "make": data.get("make", "").strip().lower().replace(" ", "-") or None,
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
        return redirect(url_for("search"))

    @app.route("/api/models")
    def api_models():
        make = request.args.get("make")
        if not make:
            return jsonify([])
        models = get_models_for_make(make)
        return jsonify(models)
