from flask import Blueprint

# Creating blueprint
carts_bp = Blueprint('carts_bp', __name__)

# It has to be here after creating blueprint
from . import routes