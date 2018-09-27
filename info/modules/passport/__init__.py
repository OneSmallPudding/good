from flask import Blueprint

blu_passport = Blueprint('passport_blu', __name__,url_prefix='/passport')
from .views import *
