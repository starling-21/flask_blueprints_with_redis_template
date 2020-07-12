from flask import Blueprint, request, make_response, jsonify
from flask import current_app as app


def construct_blueprint(redis_limiter):

    balance_bp = Blueprint('balance', __name__)

    @balance_bp.route('/', methods=["GET"])
    def index():        
        return "INDEX page"

    @balance_bp.route('/ballance', methods=["GET"])
    def curret_balance():        
        initial = redis_limiter.initial_limits
        current = redis_limiter.get_all_limits()
        response = {"limits": initial, "current": current}
        return make_response(jsonify(response), 200)

    return balance_bp
