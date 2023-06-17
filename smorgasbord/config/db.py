from ..env import env

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "base.db.dj_db_conn_pool.backends.mysql",
        "NAME": env.str("DEFAULT_MYSQL_NAME"),
        "HOST": env.str("DEFAULT_MYSQL_HOST"),
        "PORT": env.int("DEFAULT_MYSQL_PORT"),
        "USER": env.str("DEFAULT_MYSQL_USER"),
        "PASSWORD": env.str("DEFAULT_MYSQL_PASSWORD"),
        "POOL_OPTIONS": {
            "POOL_SIZE": env.int("DEFAULT_MYSQL_POOL_SIZE"),
            "MAX_OVERFLOW": env.int("DEFAULT_MYSQL_POOL_MAX_OVERFLOW"),
            "RECYCLE": env.int("DEFAULT_MYSQL_POOL_RECYCLE"),
            "PRE_PING": True,
            "ECHO": False,
            "TIMEOUT": env.int("DEFAULT_MYSQL_POOL_TIMEOUT"),
        },
    }
}
