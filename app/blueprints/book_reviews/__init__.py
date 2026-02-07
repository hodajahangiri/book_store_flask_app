from flask import Blueprint

# Creating blueprint
reviews_bp = Blueprint('reviews_bp', __name__)

# It has to be here after creating blueprint
from . import routes