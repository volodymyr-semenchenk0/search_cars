import os

from flask import Flask

from .data.options import COUNTRY_NAMES, FUEL_TYPES,COUNTRY_CODES, get_fuel_label, get_fuel_code
from .routes import register_routes


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

    @app.context_processor
    def inject_globals():
        return {
            'country_names': COUNTRY_NAMES,
            'country_codes': COUNTRY_CODES
        }

    app.jinja_env.filters['country_name'] = lambda code: COUNTRY_NAMES.get(code, code)
    app.jinja_env.filters['fuel_label'] = get_fuel_label
    app.jinja_env.filters['fuel_code']  = get_fuel_code

    register_routes(app)

    return app
