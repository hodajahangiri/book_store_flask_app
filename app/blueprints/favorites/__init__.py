from flask import Blueprint

# Creating blueprint
favorites_bp = Blueprint('favorites_bp', __name__)

# It has to be here after creating blueprint
from . import routes