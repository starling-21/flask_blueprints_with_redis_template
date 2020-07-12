from flask import Flask, Blueprint
import os
import logging
from redis.exceptions import ConnectionError

from .redis_utils.redis_limits import RedisAmountLimiter 
from .ballance import balance
from .api.api import api_bp

def create_app():
    app = Flask(__name__)
    
    init_app_config(app)
    redis_limiter = init_redis(app)

    app.redis_limiter = redis_limiter

    #registering blueprints
    balance_bp = balance.construct_blueprint(redis_limiter)
    app.register_blueprint(balance_bp)
    app.register_blueprint(api_bp)#, url_prefix="/api")

    return app


def init_app_config(app):
    from . import settings as settings
    flask_env = os.getenv("FLASK_ENV")

    if flask_env == "development":
        app.config.from_object(settings.DevelopmentConfig)
    elif flask_env == "production":
        app.config.from_object(settings.ProductionConfig)


def init_redis(app):
    """flush DB, populate redis with new testing data, set up AMOUNT_LIMIT's"""
    try:
        _redis = RedisAmountLimiter(host=os.getenv("REDIS_HOST", "192.168.99.100"), limit_name='AMOUNT_LIMITS')
        _redis.flush_all_data()
        _redis.set_initial_limits(app.config['LIMITS']['AMOUNT_LIMITS'])
    except ConnectionError as e:
        logging.log(logging.ERROR, "__REDIS CONNECTION FAILED!")
        return None   
    
    return _redis
        