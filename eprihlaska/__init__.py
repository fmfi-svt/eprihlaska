from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from .consts import MENU

nav = Nav()
items = [View(*x) for x in MENU]
nav.register_element('top', Navbar(*items))

csrf = CSRFProtect()
app = Flask(__name__)
app.config.from_object('config')
Bootstrap(app)
nav.init_app(app)
csrf.init_app(app)
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'sk'

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['sk', 'en'])

from eprihlaska import views
