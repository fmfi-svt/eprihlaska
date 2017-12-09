from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *

nav = Nav()

nav.register_element('top', Navbar(
    View('Úvod', 'index'),
    View('Osobné údaje', 'personal_info'),
    View('Ďalšie osobné údaje', 'further_personal_info'),
    View('Adresa', 'address'),
    View('Predchádzajúce štúdium', 'previous_studies'),
    View('Prijatie bez prijímacích pohovorov', 'admissions_wavers'),
))

app = Flask(__name__)
app.config.from_object('config')
Bootstrap(app)
nav.init_app(app)

from eprihlaska import views
