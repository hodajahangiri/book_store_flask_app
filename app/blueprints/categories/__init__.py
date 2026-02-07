from flask import Blueprint

# Creating blueprint
categories_bp = Blueprint('categories_bp', __name__)

# It has to be here after creating blueprint
from . import routes