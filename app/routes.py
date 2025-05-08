import datetime

from flask import render_template, request, redirect, url_for, jsonify, flash

from app.customs import CalculateCustoms
from app.data.options import FUEL_TYPES, COUNTRY_CODES, PRICE_OPTIONS, MILEAGE_OPTIONS, get_years_list
from app.parsers.autoscout24_parser import AutoScout24Parser
from app.repositories.car_repository import CarRepository
from app.services.car_service import CarService, NotFoundError, ServiceError
from app.utils.car_models_utils import get_all_makes, get_models_for_make
from app.utils.logger_config import logger

makes = get_all_makes()


def register_routes(app):
    @app.route('/')
    def index():
        raw_args = request.args.to_dict()
        clean_args = {k: v for k, v in raw_args.items() if v}
        if raw_args and raw_args != clean_args:
            return redirect(url_for('index', **clean_args))

        # Парсимо фільтри
        fields = ("make", "model", "fuel", "year", "country", "sort")
        selected = {f: request.args.get(f) for f in fields}

        # Парсимо ids для збереження вибраних авто
        ids_param = request.args.get('ids', '')
        try:
            selected_ids = [int(i) for i in ids_param.split(',') if i]
        except ValueError:
            selected_ids = []

        cars = CarService.list_cars(**selected)

        return render_template(
            'data_table.html',
            cars=cars,
            makes=makes,
            years=get_years_list(),
            fuel_types=FUEL_TYPES,
            price_options=PRICE_OPTIONS,
            mileage_options=MILEAGE_OPTIONS,
            selected=selected,
            selected_ids=selected_ids
        )

    @app.route("/search", methods=['GET', 'POST'])
    def search():
        searched = False
        saved_cars_count = 0

        if request.method == 'POST':
            data = request.form.to_dict()
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
            saved = parser.parse_autoscout24().get("saved_cars")

            redirect_args = {k: v for k, v in data.items() if v}
            redirect_args['saved'] = saved
            return redirect(url_for('search', **redirect_args))

        selected = request.args.to_dict()
        if 'saved' in selected:
            searched = True
            saved_cars_count = int(selected.pop('saved', 0))

        return render_template(
            "search.html",
            makes=makes,
            years=get_years_list(),
            fuel_types=FUEL_TYPES,
            country_codes=COUNTRY_CODES,
            price_options=PRICE_OPTIONS,
            mileage_options=MILEAGE_OPTIONS,
            searched=searched,
            saved_cars_count=int(saved_cars_count),
        )

    @app.route('/cars/<int:id>/edit', methods=['GET', 'POST'])
    def edit_car(id):
        try:
            car = CarService.get_car_details(id)
        except NotFoundError:
            logger.error('Автомобіль не знайдено.')
            return redirect(url_for('index'))

        if request.method == 'POST':
            try:
                year = int(request.form['year'])
                engine_volume = request.form.get('engine_volume')
                engine_volume = float(engine_volume) if engine_volume else None
                battery_capacity = request.form.get('battery_capacity_kwh')
                battery_capacity = float(battery_capacity) if battery_capacity else None
                price = float(request.form['price'])
            except (ValueError, KeyError):
                logger.warning('Форма заповнена не коректно')
                return render_template('edit_car.html', car=car)

            customs_uah, final_price = None, None
            calc_customs = CalculateCustoms().calculate(
                price,
                engine_volume,
                year,
                car.get('fuel_type'),
                battery_capacity_kwh=battery_capacity,
            )

            if calc_customs is not None:
                customs_uah = calc_customs.get("customs")
                final_price = calc_customs.get("total")

            update_data = {
                'year': year,
                'engine_volume': engine_volume,
                'battery_capacity_kwh': battery_capacity,
                'price': price,
                'customs_uah': customs_uah,
                'final_price_uah': final_price
            }

            try:
                CarService.update_car(id, update_data)
                logger.warning('Дані автомобіля оновлено успішно.')
                return redirect(url_for('index'))
            except ServiceError as e:
                logger.warning(f'Не вдалося оновити дані: {e}')

        return render_template('edit_car.html', car=car)

    @app.route('/cars/<int:id>/delete', methods=['POST'])
    def delete_car(id):
        try:
            CarService.remove_car(id)
            logger.info('Автомобіль успішно видалено.')
        except NotFoundError:
            logger.warning('Автомобіль не знайдено.')
        except ServiceError as e:
            logger.warning(f'Помилка при видаленні: {e}')
        return redirect(url_for('index'))

    @app.route('/duty_calc', methods=['GET', 'POST'])
    def duty_calc():
        result = None
        params = {
            'fuel_type': None,
            'price': None,
            'engine_volume': None,
            'battery_capacity_kwh': None,
            'year': None
        }

        eur_rate = CalculateCustoms().get_eur_to_uah_rate()

        if request.method == 'POST':
            try:
                fuel_type = request.form.get('fuel_type') or None
                price = float(request.form['price'])
                engine_volume = float(request.form.get('engine_volume') or 0)
                year = int(request.form['year'])
                battery_capacity_kwh = float(request.form.get('battery_capacity_kwh') or 0)
            except (ValueError, KeyError):
                flash('Будь ласка, введіть коректні значення.', 'danger')
            else:
                params.update({
                    'fuel_type': fuel_type,
                    'price': price,
                    'engine_volume': engine_volume,
                    'battery_capacity_kwh': battery_capacity_kwh,
                    'year': year
                })
                result = CalculateCustoms().calculate(
                    price,
                    engine_volume,
                    year,
                    fuel_type,
                    battery_capacity_kwh=battery_capacity_kwh
                )

        return render_template(
            'duty_calc.html',
            params=params,
            result=result,
            fuel_types=FUEL_TYPES,
            years=get_years_list(),
            eur_rate=eur_rate
        )

    @app.route('/compare')
    def compare_cars():
        ids_param = request.args.get('ids', '')
        try:
            ids = [int(i) for i in ids_param.split(',') if i]
        except ValueError:
            ids = []
        cars = CarService.get_cars_for_comparison(ids)
        # Передаємо ids_param назад для відновлення вибору при поверненні
        return render_template('compare.html', cars=cars, ids_param=ids_param)

    @app.route("/api/models")
    def api_models():
        make = request.args.get("make")
        if not make:
            return jsonify([])
        models = get_models_for_make(make)
        return jsonify(models)

