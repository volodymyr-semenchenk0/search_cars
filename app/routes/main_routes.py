from flask import render_template, request, redirect, url_for, flash, Blueprint

from app.data.options import COUNTRY_CODES, PRICE_OPTIONS, MILEAGE_OPTIONS, get_years_list
from app.services import (
    CalculateCustomsService,
    CarMakeService,
    FuelTypeService,
    NBURateService,
    OfferService,
    SourceService,
    ParseService,
)
from app.utils.normalize_filters import normalize_filters

main_bp = Blueprint('main', __name__)
makes = CarMakeService.get_all_makes_for_select()
fuel_types = FuelTypeService.list_all_fuel_types_for_select()


@main_bp.route('/')
def index():
    raw_args = request.args.to_dict()
    clean_args = {k: v for k, v in raw_args.items() if v}
    if raw_args and raw_args != clean_args:
        return redirect(url_for('main.index', **clean_args))

    # Парсимо фільтри
    fields = ("make", "model", "fuel_type", "year", "country_of_listing", "sort")
    selected = {f: request.args.get(f) for f in fields}

    # Парсимо ids для збереження вибраних авто
    ids_param = request.args.get('ids', '')
    try:
        selected_ids = [int(i) for i in ids_param.split(',') if i]
    except ValueError:
        selected_ids = []

    cars = OfferService.list_cars(**selected)

    return render_template(
        'data_table.html',
        cars=cars,
        makes=makes,
        fuel_types=fuel_types,
        years=get_years_list(),
        selected=selected,
        selected_ids=selected_ids,
    )


@main_bp.route("/search", methods=['GET', 'POST'])
def search():
    sources = SourceService.list_sources()

    if request.method == 'POST':
        data = request.form.to_dict()
        filters = normalize_filters(data)

        try:
            source_id = int(data.get('source_id'))
            ParseService.parse_website(source_id, **filters)
        except Exception as e:
            flash(str(e), 'warning')

        # redirect_params = {k: v for k, v in data.items() if v}
        return redirect(url_for('main.search'))

    selected_filters = {
        "source_id": request.args.get('source_id'),
        "make": request.args.get('make'),
        "model": request.args.get('model'),
        "pricefrom": request.args.get('pricefrom'),
        "priceto": request.args.get('priceto'),
        "fregfrom": request.args.get('fregfrom'),
        "fregto": request.args.get('fregto'),
        "kmfrom": request.args.get('kmfrom'),
        "kmto": request.args.get('kmto'),
        "cy": request.args.get('cy'),
        "fuel": request.args.get('fuel'),
    }
    selected_filters = {k: v for k, v in selected_filters.items() if v is not None}

    return render_template(
        "search.html",
        makes=makes,
        years=get_years_list(),
        fuel_types=fuel_types,
        country_codes=COUNTRY_CODES,
        price_options=PRICE_OPTIONS,
        mileage_options=MILEAGE_OPTIONS,
        sources=sources,
        selected=selected_filters
    )


@main_bp.route('/duty_calc', methods=['GET', 'POST'])
def duty_calc():
    result = None
    params = {
        'fuel_type': None,
        'price': None,
        'engine_volume': None,
        'battery_capacity_kwh': None,
        'year': None
    }

    eur_rate = NBURateService.get_eur_to_uah_rate()

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
            result = CalculateCustomsService().calculate(
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
        fuel_types=fuel_types,
        years=get_years_list(),
        eur_rate=eur_rate
    )


@main_bp.route('/compare')
def compare_cars():
    ids_param = request.args.get('ids', '')
    try:
        ids = [int(i) for i in ids_param.split(',') if i]
    except ValueError:
        ids = []
    cars = OfferService.get_cars_for_comparison(ids)
    return render_template('compare.html', cars=cars, ids_param=ids_param)
