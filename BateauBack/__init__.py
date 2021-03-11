"""
Flask JWT Example
"""

import sys
import os.path
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ
from flask_restful import Api as RestAPI

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

app.config.from_json('resources/config.json')
app.config["JWT_TOKEN_LOCATION"] = "headers"
app.config["ALEMBIC"] = False

jwt = JWTManager(app)
RestAPI = RestAPI(app)
migrate = Migrate(app, db)

from .models import * 

# override debug flag
if '--debugger' in sys.argv:
    app.debug = True

# register error handlers
from . import errors  # noqa: F401

# load & register APIs
from .api import *  # noqa: F401,F403
