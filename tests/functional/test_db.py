import unittest

from tweetgtalk import db

class DbConnectionTest(unittest.TestCase):
    
    def test_connect_to_mongo(self):
        assert db.connect()
