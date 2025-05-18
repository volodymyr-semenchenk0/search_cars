from flask import request, jsonify, Blueprint
from app.utils.logger_config import logger

from app.services import CarModelService, CountryService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route("/models")
def api_models():
    make_id_str = request.args.get("make")
    if not make_id_str:
        return jsonify([])
    try:
        make_id = int(make_id_str)
    except ValueError:
        return jsonify({"error": "Неправильний формат ID марки"}), 400

    models = CarModelService.get_models_for_make_for_select(make_id)
    return jsonify(models)


@api_bp.route("/countries")
def api_countries():
    try:
        countries = CountryService.get_countries_for_select()
        return jsonify(countries)
    except Exception as e:
        logger.error(f"API error fetching countries: {e}", exc_info=True)
        return jsonify({"error": "Could not fetch countries"}), 500