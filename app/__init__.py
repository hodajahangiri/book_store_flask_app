from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp
from .blueprints.book_descriptions import book_descriptions_bp
from .blueprints.payments import payments_bp
from .blueprints.addresses import addresses_bp
from .blueprints.categories import categories_bp
from .blueprints.book_reviews import reviews_bp
from .blueprints.favorites import favorites_bp
from .blueprints.carts import carts_bp
from .blueprints.orders import orders_bp
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

#creating swagger blueprint
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL,API_URL, config={'app_name': 'Mechanic Shop'})

def create_app(config_name):
     # Initialize flask app
     app = Flask(__name__)
     # Add config to the app
     app.config.from_object(f'config.{config_name}')

     # initialize db into flask app
     db.init_app(app)
     # Extensions     
     ma.init_app(app)
     # Add CORS To let front access to the APIs
     CORS(app)

     # Register Blueprints
     app.register_blueprint(users_bp,url_prefix='/users')
     app.register_blueprint(book_descriptions_bp, url_prefix='/book_descriptions')
     app.register_blueprint(payments_bp, url_prefix='/users/payments')
     app.register_blueprint(addresses_bp, url_prefix='/addresses')
     app.register_blueprint(categories_bp, url_prefix='/categories')
     app.register_blueprint(reviews_bp, url_prefix='/reviews')
     app.register_blueprint(favorites_bp, url_prefix='/favorites')
     app.register_blueprint(carts_bp, url_prefix='/carts')
     app.register_blueprint(orders_bp, url_prefix='/orders')
     app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)
     
     return app