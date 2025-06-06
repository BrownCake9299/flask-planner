from flask import Blueprint

plan = Blueprint('plan', __name__)

from . import views