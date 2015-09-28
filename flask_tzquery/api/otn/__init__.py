from flask import Blueprint

bp = Blueprint('otn', __name__, url_prefix="/otn")

from views import *