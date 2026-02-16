class DevelopmentConfig:
    # set the database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///book_store_app.db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 200
    

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing_book_store_app.db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 200
    TESTING = True


class ProductionConfig:
    pass