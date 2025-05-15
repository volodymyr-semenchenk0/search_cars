import os

from flask import Flask

from app.routes.api_routes import api_bp
from app.routes.cars_routes import car_bp
from app.routes.main_routes import main_bp
from .data.options import COUNTRY_NAMES, FUEL_TYPES, COUNTRY_CODES, get_fuel_label, get_fuel_code


def create_app():
    # шлях до самого this file (app/__init__.py)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # збираємо абсолютні шляхи до templates/ та static/
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.config['SECRET_KEY'] = 'a1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2W3x4Y5z6A7b8C9d0E1f2'

    @app.context_processor
    def inject_globals():
        return {
            'country_names': COUNTRY_NAMES,
            'country_codes': COUNTRY_CODES
        }

    app.jinja_env.filters['country_name'] = lambda code: COUNTRY_NAMES.get(code, code)
    app.jinja_env.filters['fuel_label'] = get_fuel_label
    app.jinja_env.filters['fuel_code'] = get_fuel_code

    app.register_blueprint(main_bp)
    app.register_blueprint(car_bp)
    app.register_blueprint(api_bp)

    return app
