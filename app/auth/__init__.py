from flask import Blueprint

# templates of 'auth should be in 'templates/auth/'
auth = Blueprint('auth', __name__, template_folder='/auth')

from . import views