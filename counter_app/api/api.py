from flask import Blueprint, jsonify, make_response
from flask import current_app as app


api_bp = Blueprint('api', __name__)


@api_bp.route('/request/<int:amount>')
def income_withdraw(amount):
    current_limits = app.redis_limiter.get_all_limits()


    result = app.redis_limiter.proceed_income_amount(amount)


    if 'result' in result.keys() and result['result'] == "OK":
        updated_limits = app.redis_limiter.get_all_limits()
        final_res = {
            "before withdrawal": current_limits,
            "withdraw_amount": amount,
            "current": updated_limits 
            }
        result.update(final_res)
        print("res:", jsonify(result))
        return make_response(jsonify(result), 200)

    print("res:", jsonify(result))
    return make_response(jsonify(result), 200)

