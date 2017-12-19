from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_nav import Nav, register_renderer
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from .consts import MENU
from .renderer import ePrihlaskaNavRenderer
import locale

nav = Nav()
items = [View(*x) for x in MENU]
nav.register_element('top', Navbar(*items))

csrf = CSRFProtect()
app = Flask(__name__)
app.config.from_object('config')
Bootstrap(app)
nav.init_app(app)
register_renderer(app, 'eprihlaska_nav_renderer', ePrihlaskaNavRenderer)

csrf.init_app(app)
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'sk_SK'
locale.setlocale(locale.LC_ALL, 'sk_SK.utf8')

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['sk_SK', 'en'])

from eprihlaska import views
