from flask import Blueprint

# Creating blueprint
orders_bp = Blueprint('orders_bp', __name__)

# It has to be here after creating blueprint
from . import routes