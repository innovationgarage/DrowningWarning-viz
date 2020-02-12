class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"

    DB_NAME = "production-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    FILE_UPLOADS = "static/files/uploads"
    FILE_PROCESSED = "static/files/processed"
    ALLOWED_CAPTURE_EXTENSIONS = ["TXT", "CSV", 'csv', 'txt']
    ALLOWED_TELESPOR_EXTENSIONS = ["CSV", 'csv']

#    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = SECRET_KEY

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    SESSION_COOKIE_SECURE = False