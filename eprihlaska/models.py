from eprihlaska import db
from flask_login import UserMixin
import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    registered_at = db.Column(db.DateTime, default=datetime.datetime.now)

class ApplicationForm(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='user')
    application = db.Column(db.Text)
    last_updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    submitted = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime)

