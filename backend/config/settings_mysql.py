from .settings import *
import pymysql

pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'trackease',
        'USER': 'root',
        'PASSWORD': 'Admin',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
