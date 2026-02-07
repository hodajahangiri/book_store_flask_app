from flask import Blueprint

# Creating blueprint
addresses_bp = Blueprint('addresses_bp', __name__)

# It has to be here after creating blueprint
from . import routes