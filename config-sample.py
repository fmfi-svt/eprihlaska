WTF_CSRF_ENABLED = True
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://eprihlaska:xxxxxxxxxxxxxxxxx@localhost/eprihlaska'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH_CLIENT_CACHE_TYPE = 'simple'
AUTHLIB_CACHE_TYPE = 'simple'

# As per https://docs.authlib.org/en/latest/client/flask.html#configuration
GOOGLE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
GOOGLE_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxx'

FACEBOOK_CLIENT_KEY = 'xxxxxxxxxxxxxx'
FACEBOOK_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxx'

MAIL_SERVER = 'mailcheck.uniba.sk'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ('ePrihlaska', 'xxxxxxxxxxxxxxxxxxxxx')

SESSION_TYPE = 'filesystem'

ADMINS = ['xxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxx']
ERROR_EMAIL_SERVER = 'mailcheck.uniba.sk'
ERROR_EMAIL_FROM = 'xxxxxxxxxxxxxxx'
ERROR_EMAIL_HEADER = 'ePrihlaska - error'

UA_CODE = 'UA-23362538-7'

MY_ENTITY_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ANDRVOTR_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

SUBMISSIONS_OPEN = True
UPLOADS_ENABLED = True

UPLOADED_RECEIPTS_DEST = 'receipts'
UPLOADED_UPFILES_DEST = 'uploaded'

MAX_CONTENT_LENGTH = 16 * 1024 * 1024
