import unittest

from tweetgtalk import config
from tweetgtalk import db

class DbConnectionTest(unittest.TestCase):
    
    def test_connect_to_mongo(self):
        assert db.connect(config.DB_NAME, 
                username=config.DB_USERNAME,
                password=config.DB_PASSWORD)

