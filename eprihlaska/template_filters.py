from eprihlaska import app

from .models import User


@app.template_filter('get_user')
def get_user_filter(user_id):
    return User.query.get(user_id)
