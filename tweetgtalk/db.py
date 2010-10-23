import mongoengine
import config

def connect():
    return mongoengine.connect(
            config.DB_NAME,
            username=config.DB_USERNAME,
            password=config.DB_PASSWORD
        )
