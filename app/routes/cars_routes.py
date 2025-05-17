from flask import render_template, request, redirect, url_for, Blueprint

from app.services import CalculateCustomsService
from app.services.car_service import CarService, NotFoundError, ServiceError
from app.utils.logger_config import logger

car_bp = Blueprint('car', __name__, url_prefix='/cars')


@car_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_car(id):
    try:
        car = CarService.get_car_details(id)
    except NotFoundError:
        logger.error('Автомобіль не знайдено.')
        return redirect(url_for('main.index'))

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
        calc_customs = CalculateCustomsService().calculate(
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
            return redirect(url_for('main.index'))
        except ServiceError as e:
            logger.warning(f'Не вдалося оновити дані: {e}')

    return render_template('edit_car.html', car=car)


@car_bp.route('/<int:id>/delete', methods=['POST'])
def delete_car(id):
    try:
        CarService.remove_car(id)
        logger.info('Автомобіль успішно видалено.')
    except NotFoundError:
        logger.warning('Автомобіль не знайдено.')
    except ServiceError as e:
        logger.warning(f'Помилка при видаленні: {e}')
    return redirect(url_for('main.index'))

