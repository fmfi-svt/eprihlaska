WTF_CSRF_ENABLED = True
SECRET_KEY = 'long-secret-key'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://eprihlaska:ia5iiyoob6evool3Ahr8@localhost/eprihlaska'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH_CLIENT_CACHE_TYPE = 'simple'
AUTHLIB_CACHE_TYPE = 'simple'

GOOGLE_CLIENT_KEY = '582782509426-8m5uj9hgbta0ec9ssk9ss23fbdf4lorc.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'sgjDA1TDgkdJg3wMg-B3XqZT'

FACEBOOK_CLIENT_KEY = '200369757178909'
FACEBOOK_CLIENT_SECRET = 'b370c3062b5dedc66755126db531ebae'

MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'prihlaska@mg.shu.io'
MAIL_PASSWORD = 'prihlaska'
MAIL_DEFAULT_SENDER = ('ePrihlaska', 'prihlaska@fmph.uniba.sk')

SESSION_TYPE = 'filesystem'
