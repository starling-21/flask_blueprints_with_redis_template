from dotenv import load_dotenv
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

# load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(verbose=True)


class Config(object):

    with open(os.path.join(basedir, 'LIMITS_CONFIG.json')) as f:
        data = json.load(f)
        LIMITS = {}
        for k, v in data.items():
            LIMITS[k] = v
            

class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
