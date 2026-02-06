from flask import Blueprint

# Creating blueprint
users_bp = Blueprint('users_bp', __name__)

# It has to be here after creating blueprint
from . import routes