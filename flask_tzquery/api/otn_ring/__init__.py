from flask import Blueprint

bp = Blueprint('otn_ring', __name__, url_prefix="/otn")

from views import *