import mocker
import unittest
from tweepy.error import TweepError

from tweetgtalk.bot import TwitterManager, TwitterAccount, MessageHandler, \
        TwitterCommands

class TwitterManagerTestCase(unittest.TestCase):
    
    def test_get_or_create_account_returns_account_if_not_exist(self):
        manager = TwitterManager()
        account = manager.get_or_create_account("igor@igorsobreira.com/Adium123")

        assert isinstance(account, TwitterAccount)

    def test_get_or_create_account_doesnt_create_duplicate_account(self):
        manager = TwitterManager()
        account1 = manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        account2 = manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        
        assert account1 == account2
        assert 1 == len(manager.accounts)

    def test_get_account_returns_none_if_no_account_found(self):
        manager = TwitterManager()
        
        assert None == manager.get_account("igor@igorsobreira.com/Aduim123")
    
    def test_get_account_returns_account(self):
        manager = TwitterManager()
        account = manager.get_or_create_account("igor@igorsobreira.com/Adium123")

        assert account == manager.get_account("igor@igorsobreira.com/Adium123")


class TwitterAccountTestCase(mocker.MockerTestCase):
    
    def test_create_account(self):
        auth = self.mocker.mock()

        tweepy = self.mocker.replace("tweepy")
        tweepy.OAuthHandler(mocker.ARGS)
        self.mocker.result(auth)
        
        self.mocker.replay()

        account = TwitterAccount('igor@igorsobreira.com/Admium123')

        self.mocker.verify()
        assert False == account.authenticating
        assert False == account.verified

    def test_authenticate(self):
        handler = self.mocker.mock()
        handler.get_authorization_url()
        self.mocker.result("http://twitter.com/authorize")

        tweepy = self.mocker.replace("tweepy")
        tweepy.OAuthHandler(mocker.ARGS)
        self.mocker.result(handler)

        self.mocker.replay()
        
        account = TwitterAccount("igor@igorsobreira.com/Adium123")
        redirect_url = account.authenticate()
        
        self.mocker.verify()

        assert "http://twitter.com/authorize" == redirect_url
        assert account.authenticating
        assert not account.verified

    def test_verify_with_valid_code(self):
        auth = self.mocker.mock()
        auth.get_access_token(mocker.ARGS)

        tweepy = self.mocker.replace("tweepy")
        tweepy.API(mocker.ARGS)
        self.mocker.result("api_instance")
        tweepy.OAuthHandler(mocker.ARGS)
        self.mocker.result(auth)
        
        self.mocker.replay()

        account = TwitterAccount("igor@igorsobreira.com/Adium123")
        verified = account.verify("code")

        self.mocker.verify()
        
        assert verified
        assert account.verified
        assert not account.authenticating

    def test_verify_with_invalid_code(self):
        auth = self.mocker.mock()
        auth.get_access_token(mocker.ARGS)
        self.mocker.throw(TweepError("error"))

        tweepy = self.mocker.replace("tweepy")
        tweepy.OAuthHandler(mocker.ARGS)
        self.mocker.result(auth)

        self.mocker.replay()

        account = TwitterAccount("igor@igorsobreira.com/Adium123")
        verified = account.verify("code")

        self.mocker.verify()
        
        assert not verified
        assert not account.verified
        assert account.authenticating


class MessageHandlerTestCase(mocker.MockerTestCase):

    def test_handle_message_from_authenticated_user(self):
        msg = self.mocker.mock()
        msg['body']
        self.mocker.result("timeline")
        msg.get_from()
        self.mocker.result("igor@igorsobreira.com/Adium123")
        
        account = self.mocker.mock()
        account.verified
        self.mocker.result(True)

        manager = self.mocker.mock()
        manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        self.mocker.result(account)

        handler = MessageHandler()
        handler.manager = manager 
        handler.execute_command = self.mocker.mock()
        handler.execute_command(account, "timeline")
        
        self.mocker.replay()

        handler.handle(msg)

        self.mocker.verify()

    def test_handle_message_from_user_with_persisted_authentication(self):
        msg = self.mocker.mock()
        msg['body']
        self.mocker.result("timeline")
        msg.get_from()
        self.mocker.result("igor@igorsobreira.com/Adium123")
        
        account = self.mocker.mock()
        account.verified
        self.mocker.result(False)
        account.reload_authentication()
        self.mocker.result(True)

        manager = self.mocker.mock()
        manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        self.mocker.result(account)

        handler = MessageHandler()
        handler.manager = manager 
        handler.execute_command = self.mocker.mock()
        handler.execute_command(account, "timeline")
        
        self.mocker.replay()

        handler.handle(msg)

        self.mocker.verify()

    def test_handle_message_to_start_authentication(self):
        msg = self.mocker.mock()
        msg['body']
        self.mocker.result("start")
        msg.get_from()
        self.mocker.result("igor@igorsobreira.com/Adium123")

        account = self.mocker.mock()
        account.verified
        self.mocker.result(False)
        account.reload_authentication()
        self.mocker.result(False)
        account.authenticating
        self.mocker.result(False)
        account.authenticate()
        self.mocker.result("/authenticate/url")
        
        manager = self.mocker.mock()
        manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        self.mocker.result(account)

        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", mocker.ARGS)
        send_message("igor@igorsobreira.com/Adium123", "/authenticate/url")
        send_message("igor@igorsobreira.com/Adium123", mocker.ARGS)
        
        self.mocker.replay()

        handler = MessageHandler()
        handler.manager = manager 
        handler.send_message = send_message
        
        handler.handle(msg)

        self.mocker.verify()
    
    def test_handle_message_with_authentication_started_and_verification_succeed(self):
        msg = self.mocker.mock()
        msg['body']
        self.mocker.result("123456")
        msg.get_from()
        self.mocker.result("igor@igorsobreira.com/Adium123")

        account = self.mocker.mock()
        account.verified
        self.mocker.result(False)
        account.reload_authentication()
        self.mocker.result(False)
        account.authenticating
        self.mocker.result(True)
        account.verify("123456")
        self.mocker.result(True)
        account.save()

        manager = self.mocker.mock()
        manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        self.mocker.result(account)

        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", "Authentication complete!")
        
        self.mocker.replay()

        handler = MessageHandler()
        handler.manager = manager 
        handler.send_message = send_message
        
        handler.handle(msg)

        self.mocker.verify()

    def test_handle_message_with_authentication_started_and_verification_fails(self):
        msg = self.mocker.mock()
        msg['body']
        self.mocker.result("123456")
        msg.get_from()
        self.mocker.result("igor@igorsobreira.com/Adium123")

        account = self.mocker.mock()
        account.verified
        self.mocker.result(False)
        account.reload_authentication()
        self.mocker.result(False)
        account.authenticating
        self.mocker.result(True)
        account.verify("123456")
        self.mocker.result(False)

        manager = self.mocker.mock()
        manager.get_or_create_account("igor@igorsobreira.com/Adium123")
        self.mocker.result(account)

        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", "Invalid verification code")
        
        self.mocker.replay()

        handler = MessageHandler()
        handler.manager = manager 
        handler.send_message = send_message
        
        handler.handle(msg)

        self.mocker.verify()
        
    def test_execute_command_not_found(self):
        account = self.mocker.mock()
        account.jid
        self.mocker.result("igor@igorsobreira.com/Adium123")
        account.api
        self.mocker.result("api")
        
        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", "Command not found")
        
        self.mocker.replay()

        handler = MessageHandler()
        handler.send_message = send_message

        handler.execute_command(account, "foobar")

        self.mocker.verify()

    def test_execute_command_timeline(self):
        account = self.mocker.mock()
        account.jid
        self.mocker.result("igor@igorsobreira.com/Adium123")
        account.api
        self.mocker.result("api")
        
        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", "@foo: bar",
                u'<a href="http://twitter.com/foo">@foo</a>: bar')
        
        home_timeline = self.mocker.mock()
        home_timeline()
        self.mocker.result( 
                ("@foo: bar", u'<a href="http://twitter.com/foo">@foo</a>: bar'))

        commands = self.mocker.mock()
        commands.resolve("timeline")
        self.mocker.result((home_timeline, {}))

        commands_class = self.mocker.mock()
        commands_class("api")
        self.mocker.result(commands)

        self.mocker.replay()

        handler = MessageHandler()
        handler.send_message = send_message
        handler.commands_class = commands_class

        handler.execute_command(account, "timeline")

        self.mocker.verify()

    def test_execute_command_tweet(self):
        account = self.mocker.mock()
        account.jid
        self.mocker.result("igor@igorsobreira.com/Adium123")
        account.api
        self.mocker.result("api")
        
        send_message = self.mocker.mock()
        send_message("igor@igorsobreira.com/Adium123", "Tweet sent")
        
        update_status = self.mocker.mock()
        update_status(tweet="this is an example tweet")
        self.mocker.result("Tweet sent")
        
        commands = self.mocker.mock()
        commands.resolve("tweet this is an example tweet")
        self.mocker.result((update_status, {"tweet": "this is an example tweet"}))

        commands_class = self.mocker.mock()
        commands_class("api")
        self.mocker.result(commands)

        self.mocker.replay()

        handler = MessageHandler()
        handler.send_message = send_message
        handler.commands_class = commands_class

        handler.execute_command(account, "tweet this is an example tweet")

        self.mocker.verify()
        

class TwitterCommandsResolverTestCase(unittest.TestCase):

    def test_resolve_timeline_command(self):
        commands = TwitterCommands("api")
        result = commands.resolve(u"timeline")
        
        assert (commands.home_timeline, {}) == result
    
    def test_ignore_extra_spaces(self):
        commands = TwitterCommands("api")
        result = commands.resolve(u"  timeline   ")

        assert (commands.home_timeline, {}) == result
    
    def test_resolve_timeline_command_paginated(self):
        commands = TwitterCommands("api")
        result = commands.resolve(u"timeline 2")
        
        assert (commands.home_timeline, {'page': '2'}) == result

    def test_resolve_tweet_comamnd(self):
        commands = TwitterCommands("api")
        result = commands.resolve(u"tweet this is a tweet")
        
        assert (commands.update_status, {'tweet': 'this is a tweet'}) == result
    
    def test_resolve_direct_message_command(self):
        commands = TwitterCommands("api")
        result = commands.resolve(u"dm @igorsobreira hello")
        
        params = {'screen_name': 'igorsobreira', 'text': 'hello'}
        assert (commands.send_direct_message, params) == result 

    def test_not_found(self):
        commands = TwitterCommands("api")
        result = commands.resolve("command not found")

        assert (commands.not_found, {}) == result
        assert u"Command not found" == commands.not_found()


class TwitterCommandsTestCase(mocker.MockerTestCase):
    
    def _tweet(self, username, message):
        user = self.mocker.mock()
        user.screen_name
        self.mocker.result(username)

        status = self.mocker.mock()
        status.user
        self.mocker.result(user)
        status.text
        self.mocker.result(message)
        return status

    def test_timeline_command(self):
        status1 = self._tweet('igorsobreira', 'Just a simple tweet')
        status2 = self._tweet('somebody', 'Just another tweet')

        api = self.mocker.mock()
        api.home_timeline(page=1)
        self.mocker.result([status1, status2])

        self.mocker.replay()

        commands = TwitterCommands(api)
        text, html = commands.home_timeline()

        self.mocker.verify()
        assert '@igorsobreira: Just a simple tweet\n\n@somebody: Just another tweet' == text
        
        expected_html =  '<a href="http://twitter.com/igorsobreira">@igorsobreira</a>: '
        expected_html += 'Just a simple tweet<br/><br/>'
        expected_html += '<a href="http://twitter.com/somebody">@somebody</a>: '
        expected_html += 'Just another tweet'
        
        assert expected_html == html
    
    def test_timeline_command_paginated(self):
        status1 = self._tweet('igorsobreira', 'Just a simple tweet')
        status2 = self._tweet('somebody', 'Just another tweet')

        api = self.mocker.mock()
        api.home_timeline(page=1)
        self.mocker.result([status1])
        api.home_timeline(page=2)
        self.mocker.result([status2])

        self.mocker.replay()

        commands = TwitterCommands(api)
        text1, html1 = commands.home_timeline()
        text2, html2 = commands.home_timeline(page=2)

        self.mocker.verify()
        
        expected_html1 =  '<a href="http://twitter.com/igorsobreira">@igorsobreira</a>: '
        expected_html1 += 'Just a simple tweet'
        
        assert "@igorsobreira: Just a simple tweet" == text1
        assert expected_html1 == html1

        expected_html2 = '<a href="http://twitter.com/somebody">@somebody</a>: '
        expected_html2 += 'Just another tweet'
        
        assert "@somebody: Just another tweet" == text2
        assert expected_html2 == html2

    def test_tweet_command(self):
        api = self.mocker.mock()
        api.update_status(u"this is a tweet to test the api")
        
        self.mocker.replay()

        commands = TwitterCommands(api)
        result = commands.update_status(u"this is a tweet to test the api")
        
        self.mocker.verify()
        assert u"Tweet sent" == result
    
    def test_tweet_command_ignores_empty_tweets(self):
        commands = TwitterCommands("api")
        result = commands.update_status("  ")
        
        assert u"Empty tweet" == result

    def test_tweet_command_validate_length(self):
        api = self.mocker.mock()
        
        self.mocker.replay()

        commands = TwitterCommands(api)
        result = commands.update_status(u"o"*141)
        
        self.mocker.verify()
        assert u"Tweet too long, 141 characters. Must be up to 140." == result
    
    def test_direct_message_command(self):
        api = self.mocker.mock()
        api.send_direct_message(screen_name="igorsobreira", text="hello")

        self.mocker.replay()

        commands = TwitterCommands(api)
        result = commands.send_direct_message(screen_name='igorsobreira', text='hello')

        self.mocker.verify()
        assert u"Message sent" == result

    def test_direct_message_error_when_trying_to_send_to_non_friends(self):
        api = self.mocker.mock()
        api.send_direct_message(screen_name="unknown", text="hello")
        self.mocker.throw(TweepError(u"You cannot send messages to users who are not following you."))

        self.mocker.replay()

        commands = TwitterCommands(api)
        result = commands.send_direct_message(screen_name='unknown', text='hello')

        self.mocker.verify()
        assert u"You cannot send messages to users who are not following you." == result
