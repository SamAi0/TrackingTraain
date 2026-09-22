from .settings import *
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_HOST',
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}
