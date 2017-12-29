from flask import Flask, request, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav, register_renderer
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

from .consts import MENU
from .renderer import (ePrihlaskaNavRenderer, ExtendedNavbar, UserGreeting,
                       LogInLogOut)
import locale

nav = Nav()
items = [View(*x) for x in MENU]
right_items = [UserGreeting(), LogInLogOut()]
nav.register_element('top', ExtendedNavbar(title=items[0],
                                           items=items[1:],
                                           right_items=right_items))

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

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from .models import User
@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))


from eprihlaska import views
