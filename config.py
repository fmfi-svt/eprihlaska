WTF_CSRF_ENABLED = True
SECRET_KEY = 'long-secret-key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH_CLIENT_CACHE_TYPE = 'simple'
AUTHLIB_CACHE_TYPE = 'simple'

GOOGLE_CLIENT_KEY = ''
GOOGLE_CLIENT_SECRET = ''

FACEBOOK_CLIENT_KEY = ''
FACEBOOK_CLIENT_SECRET = ''

MAIL_SERVER = ''
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ('ePrihlaska', 'prihlaska@fmph.uniba.sk')

SESSION_TYPE = 'filesystem'

ADMINS = []
ERROR_EMAIL_SERVER = ''
ERROR_EMAIL_FROM = 'prihlaska@fmph.uniba.sk'
ERROR_EMAIL_HEADER = 'ePrihlaska - error'

UA_CODE = ''

COSIGN_PROXY_DIR = ''
