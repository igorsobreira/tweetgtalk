import mocker 
import tweepy

from tweetgtalk.models import User
from tweetgtalk.bot import TwitterAccount
from tweetgtalk import db

class TwitterAccountTestCase(mocker.MockerTestCase):
    
    def setUp(self):
        db.connect()
        User.objects.delete()

    def build_token_mock(self, data):
        token_mock = self.mocker.mock()
        token_mock.to_string()
        self.mocker.result(data)
        return token_mock


    def test_save_method(self):
        token_mock = self.build_token_mock("dnlksn12lndsn1lsdn1elndn")
        self.mocker.replay()

        account = TwitterAccount(jid="igor@igorsobreira.com/Adium123")
        account._token = token_mock
        account.save()
        
        self.mocker.verify()
        assert 1 == User.objects(jid="igor@igorsobreira.com").count()
        assert 1 == User.objects(token="dnlksn12lndsn1lsdn1elndn").count()

    def test_save_method_updates_token_if_user_already_exists(self):
        token_mock1 = self.build_token_mock("dnjabndakjbdajsdbas")
        token_mock2 = self.build_token_mock("12nkn21kn1lk2nkl1n2")
        self.mocker.replay()

        account1 = TwitterAccount(jid="igor@igorsobreira.com/Adium123")
        account1._token = token_mock1
        account1.save()

        account2 = TwitterAccount(jid="igor@igorsobreira.com/Psi456")
        account2._token = token_mock2
        account2.save()
        
        self.mocker.verify()

        assert 1 == User.objects(jid="igor@igorsobreira.com").count()
        assert 1 == User.objects(token="12nkn21kn1lk2nkl1n2").count()
    
    def test_reload_authentication_method(self):
        token_mock = self.build_token_mock("oauth_token_secret=secret&oauth_token=token")
        self.mocker.replay()

        account = TwitterAccount(jid="igor@igorsobreira.com/Adium123")
        account._token = token_mock
        
        assert not account.reload_authentication()
        
        account.save()
        
        assert account.reload_authentication()

        account.reload_authentication()

        assert "secret" == account._token.secret
        assert "token" == account._token.key
        assert isinstance(account.api, tweepy.API)
