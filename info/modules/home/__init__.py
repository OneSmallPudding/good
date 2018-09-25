from flask import Blueprint

blu_home = Blueprint('home_blu', __name__)
from .views import *
