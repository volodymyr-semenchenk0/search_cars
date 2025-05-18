from flask import render_template, request, redirect, url_for, flash, Blueprint, session

from app.data.options import PRICE_OPTIONS, MILEAGE_OPTIONS, get_years_list
from app.services import (
    CalculateCustomsService,
    CarMakeService,
    FuelTypeService,
    NBURateService,
    OfferService,
    SourceService,
    ParseService
)
from app.utils.logger_config import logger
from app.utils.normalize_filters import normalize_filters

main_bp = Blueprint('main', __name__)
makes = CarMakeService.get_all_makes_for_select()
fuel_types = FuelTypeService.list_all_fuel_types_for_select()


@main_bp.route('/history')
def get_history_data():
    raw_args = request.args.to_dict()
    clean_args = {k: v for k, v in raw_args.items() if v}
    if raw_args and raw_args != clean_args:
        return redirect(url_for('main.get_history_data', **clean_args))

    fields = ("make", "model", "fuel_type", "year", "country", "sort")
    selected = {f: request.args.get(f) for f in fields}

    ids_param = request.args.get('ids', '')
    try:
        selected_ids = [int(i) for i in ids_param.split(',') if i]
    except ValueError:
        selected_ids = []

    cars = OfferService.get_filtered_cars_list(**selected)

    return render_template(
        'data_table.html',
        cars=cars,
        makes=makes,
        fuel_types=fuel_types,
        years=get_years_list(),
        selected=selected,
        selected_ids=selected_ids,
    )


@main_bp.route("/", methods=['GET', 'POST'])
def search():
    sources = SourceService.list_sources()
    newly_found_offers = []

    current_form_values = request.form.to_dict() if request.method == 'POST' else request.args.to_dict()

    if request.method == 'POST':
        raw_form_data_post = request.form.to_dict()
        filters = normalize_filters(raw_form_data_post)

        try:
            source_id = int(raw_form_data_post.get('source_id'))

            saved_cars_count, newly_saved_ids = ParseService.parse_website(source_id, **filters)

            if newly_saved_ids:
                session['newly_found_ids'] = newly_saved_ids
                session['results_originated_from_post'] = True
                flash(f"Збережено {saved_cars_count} нових оголошень.", 'success')
            else:
                flash("Нічого нового не знайдено або все вже є в базі.", 'info')
        except Exception as e:
            flash("Помилка при пошуку", "danger")
            logger.exception(e)

        return redirect(url_for('main.search', **raw_form_data_post))

    else:
        selected_values_for_template = current_form_values or request.args.to_dict()

        referer = request.referrer or ''
        if not referer.endswith('/search'):
            session.pop('results_originated_from_post', None)
            session.pop('newly_found_ids', None)

        if session.get('results_originated_from_post'):
            ids_from_session = session.get('newly_found_ids', [])
            if ids_from_session:
                newly_found_offers = OfferService.get_offers_list_by_ids(ids_from_session)

    return render_template(
        "search.html",
        makes=makes,
        years=get_years_list(),
        fuel_types=fuel_types,
        price_options=PRICE_OPTIONS,
        mileage_options=MILEAGE_OPTIONS,
        sources=sources,
        selected=selected_values_for_template,
        newly_found_offers=newly_found_offers,
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
