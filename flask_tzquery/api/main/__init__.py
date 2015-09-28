#-*-coding:utf8-*-
from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix="/")

from views import *