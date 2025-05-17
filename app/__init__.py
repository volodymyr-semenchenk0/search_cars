import os

from dotenv import load_dotenv
from flask import Flask

from app.routes.api_routes import api_bp
from app.routes.cars_routes import car_bp
from app.routes.main_routes import main_bp
from .data.options import COUNTRY_NAMES, FUEL_TYPES, COUNTRY_CODES, get_fuel_label, get_fuel_code

load_dotenv()

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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
