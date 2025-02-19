from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_nav3 import Nav, register_renderer
from flask_nav3.elements import View
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session

from authlib.integrations.flask_client import OAuth

from flask_uploads import configure_uploads
from .consts import MENU, receipts, uploaded_files
from .renderer import ePrihlaskaNavRenderer, ExtendedNavbar, UserGreeting, LogInLogOut
import locale

import logging
from logging.handlers import SMTPHandler
from logging import Formatter


nav = Nav()
items = [View(*x) for x in MENU]
right_items = [UserGreeting(), LogInLogOut()]
nav.register_element(
    "top", ExtendedNavbar(title=items[0], items=items[1:], right_items=right_items)
)

csrf = CSRFProtect()
app = Flask(__name__)
app.config.from_object("config")
Bootstrap(app)
nav.init_app(app)
register_renderer(app, "eprihlaska_nav_renderer", ePrihlaskaNavRenderer)

csrf.init_app(app)


def get_locale():
    return request.accept_languages.best_match(["sk_SK", "en"])


babel = Babel(app, locale_selector=get_locale)
app.config["BABEL_DEFAULT_LOCALE"] = "sk_SK"
locale.setlocale(locale.LC_ALL, "sk_SK.utf8")

configure_uploads(app, receipts)
configure_uploads(app, uploaded_files)

mail_handler = SMTPHandler(
    mailhost=app.config["ERROR_EMAIL_SERVER"],
    fromaddr=app.config["ERROR_EMAIL_FROM"],
    toaddrs=app.config["ADMINS"],
    subject=app.config["ERROR_EMAIL_HEADER"],
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(
    Formatter(
        """
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
"""
    )
)

if not app.debug:
    app.logger.addHandler(mail_handler)


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from .models import User, fetch_token  # noqa


@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))


CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth = OAuth(app)
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
    fetch_token=fetch_token,
)

mail = Mail(app)
sess = Session(app)

from eprihlaska import views  # noqa
