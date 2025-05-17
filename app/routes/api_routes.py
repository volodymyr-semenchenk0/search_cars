from flask import request, jsonify, Blueprint

from app.services import CarModelService

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
