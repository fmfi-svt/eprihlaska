from flask import Flask, request, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav, register_renderer
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_mail import Mail
from flask_session import Session

from authlib.flask.client import OAuth
from authlib.client.apps import google, facebook

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
try:
   locale.setlocale(locale.LC_ALL, 'sk_SK.utf8')
except Exception:
   try:
      locale.setlocale(locale.LC_ALL, 'sk_SK.UTF-8')
   except Exception as e:
      pass
#        message.error(request, 'An error occurred: {0}'.format(e))

import logging
from logging.handlers import SMTPHandler
from logging import Formatter

mail_handler = SMTPHandler(
    mailhost=app.config['ERROR_EMAIL_SERVER'],
    fromaddr=app.config['ERROR_EMAIL_FROM'],
    toaddrs=app.config['ADMINS'],
    subject=app.config['ERROR_EMAIL_HEADER']
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))

if not app.debug:
    app.logger.addHandler(mail_handler)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['sk_SK', 'en'])

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from .models import User, fetch_token
@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))

oauth = OAuth(fetch_token=fetch_token)
oauth.init_app(app)
google.register_to(oauth)
facebook.register_to(oauth)

mail = Mail(app)
sess = Session(app)

from eprihlaska import views
