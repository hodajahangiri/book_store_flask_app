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
     app.register_blueprint(book_descriptions_bp, url_prefix='/book_descriptions')
     app.register_blueprint(payments_bp, url_prefix='/users/payments')
     app.register_blueprint(addresses_bp, url_prefix='/addresses')
     app.register_blueprint(categories_bp, url_prefix='/categories')
     app.register_blueprint(reviews_bp, url_prefix='/reviews')
     app.register_blueprint(favorites_bp, url_prefix='/favorites')
     app.register_blueprint(carts_bp, url_prefix='/carts')
     
     return app