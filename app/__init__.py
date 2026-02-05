from flask import Flask
from .models import db
from .extensions import ma

def create_app(config_name):
     # Initialize flask app
    app = Flask(__name__)
    # Add config to the app
    app.config.from_object(f'config.{config_name}')

    # initialize db into flask app
    db.init_app(app)
    ma.init_app(app)

    return app