from flask import Blueprint

# Creating blueprint
book_descriptions_bp = Blueprint('book_descriptions_bp', __name__)

# It has to be here after creating blueprint
from . import routes