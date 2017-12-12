import os
python_home = os.path.dirname(os.path.abspath(__file__)) + '/venv'

activate_this = python_home + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from eprihlaska import app as application
