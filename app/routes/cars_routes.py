from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify

from app.data.options import get_years_list
from app.services import OfferService, NotFoundError, ServiceError
from app.utils.logger_config import logger

car_bp = Blueprint('car', __name__, url_prefix='/cars')


@car_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_car(id: int):
    try:
        offer_details = OfferService.get_offer_details(id)
    except NotFoundError:
        flash('Оголошення не знайдено.', 'danger')
        logger.warning(f"Спроба редагування неіснуючого оголошення ID {id} (NotFoundError).")
        return redirect(url_for('main.get_history_data'))

    if not offer_details:
        flash('Оголошення не знайдено (деталі відсутні).', 'danger')
        logger.warning(f"Спроба редагування оголошення ID {id}, але деталі не отримано.")
        return redirect(url_for('main.get_history_data'))

    if request.method == 'POST':
        try:
            data_for_update = {
                "offer_id": id,
                "car_id": offer_details.get('car_id'),
                "powertrain_id": offer_details.get('powertrain_id'),
                "raw_fuel_type": offer_details.get('fuel_type'),
            }

            form_price_eur = request.form.get('price_eur')
            if form_price_eur:
                data_for_update["price_eur"] = float(form_price_eur)

            form_production_year = request.form.get('production_year')
            if form_production_year:
                data_for_update["production_year"] = int(form_production_year)

            form_engine_volume_cc = request.form.get('engine_volume_cc')
            data_for_update["engine_volume_cc"] = float(form_engine_volume_cc) if form_engine_volume_cc else None

            form_battery_capacity_kwh = request.form.get('battery_capacity_kwh')
            data_for_update["battery_capacity_kwh"] = float(
                form_battery_capacity_kwh) if form_battery_capacity_kwh else None

            if data_for_update.get("price_eur") is None or data_for_update.get("production_year") is None:
                flash('Рік виробництва та ціна є обов\'язковими для оновлення.', 'warning')
                current_form_data = {
                    'price': data_for_update.get("price_eur"),
                    'production_year': data_for_update.get("production_year"),
                    'engine_volume_cc': data_for_update.get("engine_volume_cc"),
                    'battery_capacity_kwh': data_for_update.get("battery_capacity_kwh"),
                }

                render_data = {**offer_details, **current_form_data}
                return render_template('edit_car.html', car=render_data, years=get_years_list())

            logger.info(f"Підготовлено дані для оновлення оголошення ID {id}: {data_for_update}")

            if OfferService.update_offer_and_details(data_for_update):
                flash('Оголошення успішно оновлено.', 'success')
                logger.info(f"Оголошення ID {id} успішно оновлено.")
                return redirect(url_for('main.get_history_data'))
            else:
                flash('Не вдалося оновити оголошення. Можливо, дані не змінилися або сталася помилка.', 'warning')
                logger.warning(f"Оновлення оголошення ID {id} не призвело до змін або повернуло False.")

        except ValueError:
            flash('Будь ласка, введіть коректні числові значення для ціни, року, об\'єму або ємності.', 'danger')
            logger.warning(f"Помилка ValueError при обробці форми редагування для ID {id}.")
        except ServiceError as e:
            flash(f'Помилка сервісу при оновленні: {str(e)}', 'danger')
            logger.error(f'Помилка ServiceError при оновленні оголошення ID {id}: {e}', exc_info=True)
        except Exception as e:
            logger.critical(f'Непередбачена помилка Exception при оновленні оголошення ID {id}: {e}', exc_info=True)
            flash('Виникла непередбачена помилка при оновленні оголошення.', 'danger')
        return render_template('edit_car.html', car=offer_details, years=get_years_list())

    return render_template('edit_car.html', car=offer_details, years=get_years_list())


@car_bp.route('/<int:id>/delete', methods=['POST'])
def delete_car(id):
    try:
        OfferService.remove_offer(id)
        flash('Оголошення успішно видалено.', 'success')
        logger.info(f'Оголошення ID {id} успішно видалено.')
    except NotFoundError:
        flash('Оголошення не знайдено для видалення.', 'danger')
        logger.warning(f'Оголошення ID {id} не знайдено (NotFoundError).')
    except Exception as e:
        flash('Помилка при видаленні оголошення.', 'danger')
        logger.error(f'Помилка при AJAX-видаленні ID {id}: {e}', exc_info=True)

    return render_template('partial/flash_messages.html')

@car_bp.route('/compare')
def compare_cars():
    ids_str = request.args.get('ids')
    if not ids_str:
        flash('Не обрано автомобілі для порівняння.', 'warning')
        return redirect(url_for('main.get_history_data'))

    try:
        offer_ids = [int(id_val.strip()) for id_val in ids_str.split(',') if id_val.strip().isdigit()]
    except ValueError:
        flash('Некоректний формат ID для порівняння.', 'danger')
        return redirect(url_for('main.get_history_data'))

    if not offer_ids or len(offer_ids) < 1 :
        flash('Для порівняння потрібно обрати хоча б один автомобіль (зазвичай два або більше).', 'warning')


    cars_to_compare = OfferService.get_offers_list_by_ids(offer_ids)

    if not cars_to_compare:
        flash('Не вдалося знайти обрані автомобілі для порівняння.', 'info')

    return render_template('compare.html', cars=cars_to_compare, ids_param=ids_str)