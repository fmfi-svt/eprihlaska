WTF_CSRF_ENABLED = True
SECRET_KEY = 'te4EeGoh1axee3Nah5iwaimoogahBeithoh5ieyaanooH4Zumoox8ooQuoo8'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://eprihlaska:ia5iiyoob6evool3Ahr8@localhost/eprihlaska'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH_CLIENT_CACHE_TYPE = 'simple'
AUTHLIB_CACHE_TYPE = 'simple'

GOOGLE_CLIENT_KEY = '469275337651-7jpkkecvs0d9rldt3b0mjjaf7voe6rv5.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '8piOFgrJJpudab-XKvK_x813'

FACEBOOK_CLIENT_KEY = '327870741042548'
FACEBOOK_CLIENT_SECRET = '3ce3d27f9afcfc1014c7f3cff5a092c8'

MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'prihlaska@mg.shu.io'
MAIL_PASSWORD = 'prihlaska'
MAIL_DEFAULT_SENDER = ('ePrihlaska', 'prihlaska@fmph.uniba.sk')

SESSION_TYPE = 'filesystem'
