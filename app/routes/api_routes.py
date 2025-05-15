from flask import request, jsonify, Blueprint

from app.utils.car_models_utils import get_models_for_make

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/models")
def api_models():
    make = request.args.get("make")
    if not make:
        return jsonify([])
    models = get_models_for_make(make)
    return jsonify(models)
