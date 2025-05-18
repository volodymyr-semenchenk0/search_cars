# app/routes/cars_routes.py
from flask import render_template, request, redirect, url_for, Blueprint, flash

# ... (інші імпорти)
from app.services import OfferService, NotFoundError, ServiceError, CalculateCustomsService # Додано CalculateCustomsService
from app.data.options import get_years_list # Додано get_years_list
from app.utils.logger_config import logger

car_bp = Blueprint('car', __name__, url_prefix='/cars')

@car_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_car(id: int):
    try:
        offer_details = OfferService.get_offer_details(id)
    except NotFoundError:
        flash('Оголошення не знайдено.', 'danger')
        logger.warning(f"Спроба редагування неіснуючого оголошення ID {id} (NotFoundError).")
        return redirect(url_for('main.index'))

    if not offer_details:
        flash('Оголошення не знайдено (деталі відсутні).', 'danger')
        logger.warning(f"Спроба редагування оголошення ID {id}, але деталі не отримано.")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # Збираємо дані з форми та з оригінальних деталей оголошення
            data_for_update = {
                "offer_id": id,
                "car_id": offer_details.get('car_id'),
                "powertrain_id": offer_details.get('powertrain_id'),
                "raw_fuel_type": offer_details.get('fuel_type'), # `fuel_type` з get_offer_details це key_name
            }

            # Оновлюємо значеннями з форми, якщо вони є
            form_price_eur = request.form.get('price_eur')
            if form_price_eur:
                data_for_update["price_eur"] = float(form_price_eur)

            form_production_year = request.form.get('production_year')
            if form_production_year:
                data_for_update["production_year"] = int(form_production_year)

            # Для полів, що можуть бути відсутні або порожні (наприклад, для електрокарів/ДВЗ)
            form_engine_volume_cc = request.form.get('engine_volume_cc')
            data_for_update["engine_volume_cc"] = float(form_engine_volume_cc) if form_engine_volume_cc else None

            form_battery_capacity_kwh = request.form.get('battery_capacity_kwh')
            data_for_update["battery_capacity_kwh"] = float(form_battery_capacity_kwh) if form_battery_capacity_kwh else None

            # Валідація, чи є обов'язкові поля для сервісу
            if data_for_update.get("price_eur") is None or data_for_update.get("production_year") is None:
                flash('Рік виробництва та ціна є обов\'язковими для оновлення.', 'warning')
                # Повертаємо користувача до форми з вже введеними даними (якщо вони є)
                # та оригінальними даними для решти полів
                current_form_data = {
                    'price': data_for_update.get("price_eur"),
                    'production_year': data_for_update.get("production_year"),
                    'engine_volume_cc': data_for_update.get("engine_volume_cc"),
                    'battery_capacity_kwh': data_for_update.get("battery_capacity_kwh"),
                }
                # Поєднуємо оригінальні дані з тим, що користувач міг ввести
                render_data = {**offer_details, **current_form_data}
                return render_template('edit_car.html', car=render_data, years=get_years_list())


            logger.info(f"Підготовлено дані для оновлення оголошення ID {id}: {data_for_update}")

            if OfferService.update_offer_and_details(data_for_update):
                flash('Оголошення успішно оновлено.', 'success')
                logger.info(f"Оголошення ID {id} успішно оновлено.")
                return redirect(url_for('main.index'))
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

        # У випадку помилки POST запиту, повторно рендеримо сторінку з поточними деталями
        # (які могли бути частково змінені в data_for_update перед помилкою, але ще не збережені)
        # Краще передавати оригінальні offer_details, якщо не хочемо показувати незбережені зміни
        return render_template('edit_car.html', car=offer_details, years=get_years_list())

    # GET запит
    return render_template('edit_car.html', car=offer_details, years=get_years_list())


@car_bp.route('/<int:id>/delete', methods=['POST'])
def delete_car(id):
    # ... (існуючий код delete_car)
    try:
        OfferService.remove_offer(id)
        flash('Оголошення успішно видалено.', 'success')
        logger.info(f'Оголошення ID {id} успішно видалено.')

    except NotFoundError:
        flash('Оголошення не знайдено для видалення.', 'danger')
        logger.warning(f'Спроба видалити неіснуюче оголошення ID {id} (NotFoundError).')
    except ServiceError as e:
        flash(f'Помилка сервісу при видаленні оголошення: {str(e)}', 'danger')
        logger.error(f'Помилка сервісу ServiceError при видаленні оголошення ID {id}: {e}', exc_info=True)
    except Exception as e:
        flash(f'Виникла непередбачена помилка при видаленні оголошення.', 'danger')
        logger.critical(f'Непередбачена помилка Exception при видаленні оголошення ID {id}: {e}', exc_info=True)

    return redirect(url_for('main.index'))