from localsettings import *

TEMPLATE_DEBUG = DEBUG

MANAGERS = ADMINS

db_engine = {
    'mysql': 'mysql',
    'oracle': 'oracle',
    'postgresql': 'postgresql_psycopg2',
    'sqlite': 'sqlite3'
}[DB_TYPE]


DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

TEMPLATE_DIRS = (
    '%s/templates' % OMOMA_DIR,
)

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dialog/loginok'

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''

STATIC_ROOT = '%s/consolidatedstatic/' % OMOMA_DIR
STATIC_URL = '/static/'
STATICFILES_DIRS = (
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'gadjo.requestprovider.middleware.RequestProvider',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

ROOT_URLCONF = 'omoma.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'omoma',
    'omoma.foundations',
    'omoma.transactions',
    'omoma.community',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'south',
    # Remove the next one when lipsum is not needed anymore
    'django.contrib.webdesign'
)

AUTH_PROFILE_MODULE = 'foundations.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

ANONYMOUS_USER_ID = 1
