from eprihlaska import db
from flask import json, request
from flask_login import UserMixin, current_user
import datetime
import time
from .consts import ApplicationStates


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(180))
    registered_at = db.Column(db.DateTime, default=datetime.datetime.now)


def application_form_change_author():
    remote_user = request.environ.get("REMOTE_USER")
    if remote_user is not None:
        return remote_user
    else:
        return "user"


class ApplicationForm(db.Model):
    __tablename__ = "application_form"
    __table_args__ = {"sqlite_autoincrement": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="user")
    application = db.Column(db.Text)
    last_updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    last_updated_by = db.Column(
        db.String(50), default="user", onupdate=application_form_change_author
    )
    submitted_at = db.Column(db.DateTime)
    processed_at = db.Column(db.DateTime)
    printed_at = db.Column(db.DateTime)
    state = db.Column(db.Enum(ApplicationStates), default=ApplicationStates.in_progress)


class ForgottenPasswordToken(db.Model):
    hash = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    valid = db.Column(db.Boolean, default=True)
    valid_until = db.Column(db.DateTime)


class TokenModel(db.Model):
    __tablename__ = "connect"
    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uc_connect"),)
    OAUTH1_TOKEN_TYPE = "oauth1.0"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    token_type = db.Column(db.String(20))
    # Google OAuth access tokens can exceed 255 chars; use Text to avoid truncation.
    access_token = db.Column(db.Text, nullable=False)
    # refresh_token or access_token_secret
    alt_token = db.Column(db.Text)
    extras = db.Column(db.Text)
    expires_at = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        if self.token_type == self.OAUTH1_TOKEN_TYPE:
            return dict(
                oauth_token=self.access_token,
                oauth_token_secret=self.alt_token,
            )
        return dict(
            access_token=self.access_token,
            refresh_token=self.alt_token,
            token_type=self.token_type,
            expires_at=self.expires_at,
        )

    @classmethod
    def save(cls, name, token, user):
        data = token.copy()
        conn = cls.query.filter_by(user_id=user.id, name=name).first()
        if not conn:
            conn = cls(user_id=user.id, name=name)

        if "oauth_token" in data:
            # save for OAuth 1
            conn.token_type = cls.OAUTH1_TOKEN_TYPE
            conn.access_token = data.pop("oauth_token")
            conn.alt_token = data.pop("oauth_token_secret")
            conn.extras = json.dumps(data)
        else:
            conn.access_token = data.pop("access_token")
            conn.token_type = data.pop("token_type", "")
            conn.alt_token = data.pop("refresh_token", "")
            expires_in = data.pop("expires_in", 0)
            if expires_in:
                conn.expires_at = int(time.time()) + expires_in
            conn.extras = json.dumps(data)

        db.session.add(conn)
        db.session.commit()
        return conn


def fetch_token(name):
    user = current_user
    conn = TokenModel.query.filter_by(user_id=user.id, name=name).first()
    return conn.to_dict()
