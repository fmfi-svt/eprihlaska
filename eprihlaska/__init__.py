from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect

nav = Nav()

nav.register_element('top', Navbar(
    View('Úvod', 'index'),
    View('Osobné údaje', 'personal_info'),
    View('Ďalšie osobné údaje', 'further_personal_info'),
    View('Adresa', 'address'),
    View('Predchádzajúce štúdium', 'previous_studies'),
    View('Prijatie bez prijímacích pohovorov', 'admissions_wavers'),
))
csrf = CSRFProtect()
app = Flask(__name__)
app.config.from_object('config')
Bootstrap(app)
nav.init_app(app)
csrf.init_app(app)

from eprihlaska import views
