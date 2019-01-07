WTF_CSRF_ENABLED = True
SECRET_KEY = 'UumuV3neeGouluut7eirOhk8ushi0aizei0ieteeeeT0laiLie6EetahX8Ei'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://eprihlaska:Er5phaLixie1raPhaipe@localhost/eprihlaska'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH_CLIENT_CACHE_TYPE = 'simple'
AUTHLIB_CACHE_TYPE = 'simple'

GOOGLE_CLIENT_KEY = '469275337651-7jpkkecvs0d9rldt3b0mjjaf7voe6rv5.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '8piOFgrJJpudab-XKvK_x813'

FACEBOOK_CLIENT_KEY = '327870741042548'
FACEBOOK_CLIENT_SECRET = '3ce3d27f9afcfc1014c7f3cff5a092c8'

MAIL_SERVER = 'mailcheck.uniba.sk'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ('ePrihlaska', 'prijimacky@fmph.uniba.sk')

SESSION_TYPE = 'filesystem'

ADMINS = ['mareksuppa@gmail.com', 'ado.matejov@gmail.com', 'tvinar@gmail.com']
ERROR_EMAIL_SERVER = 'mailcheck.uniba.sk'
ERROR_EMAIL_FROM = 'prihlaska@fmph.uniba.sk'
ERROR_EMAIL_HEADER = 'ePrihlaska - error'

UA_CODE = 'UA-23362538-7'

COSIGN_PROXY_DIR = '/opt/cosign/proxy'

SUBMISSIONS_OPEN = True

UPLOADED_RECEIPTS_DEST = 'receipts'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
