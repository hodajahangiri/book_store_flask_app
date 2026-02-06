from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp

def create_app(config_name):
     # Initialize flask app
     app = Flask(__name__)
     # Add config to the app
     app.config.from_object(f'config.{config_name}')

     # initialize db into flask app
     db.init_app(app)
     # Extensions     
     ma.init_app(app)

     # Register Blueprints
     app.register_blueprint(users_bp,url_prefix='/users')


     return app