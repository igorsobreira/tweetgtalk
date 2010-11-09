#!/usr/bin/env python
import re
import tweepy
import sleekxmpp
from sleekxmpp.xmlstream import ET

import config
import db
from models import User

class TweetBot(sleekxmpp.ClientXMPP):
    '''
    Handle XMPP logic
    '''

    def __init__(self, jid, password):
        super(TweetBot, self).__init__(jid, password)
        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)
        
        self.message_handler = MessageHandler(bot=self)

    def on_start(self, event):
        self.sendPresence()

    def on_message(self, msg):
        if msg['type'] == 'chat' and msg['body']:
            self.message_handler.handle(msg)


class MessageHandler(object):
    '''
    Handle incomming messages routing to commands or authentication
    '''

    def __init__(self, bot=None):
        self.bot = bot
        self.manager = TwitterManager()
        self.commands_class = TwitterCommands

    def handle(self, msg):
        body = msg['body'].strip()
        jid = str(msg.get_from())

        account = self.manager.get_or_create_account(jid)
        if account.verified or account.reload_authentication():
            self.execute_command(account, body)
        else: 
            if account.authenticating:
                if account.verify(body):
                    self.send_message(jid, 'Authentication complete!')
                    account.save()
                else:
                    self.send_message(jid, 'Invalid verification code')
            else:
                redirect_url = account.authenticate()
                self.send_message(jid, u'Enter the url bellow and click "Allow"')
                self.send_message(jid, redirect_url)
                self.send_message(jid, u'Enter de verification code:')
    
    def execute_command(self, account, message):
        commands = self.commands_class(account.api)
        command, kwargs = commands.resolve(message)
        result = command(**kwargs)
        if isinstance(result, (list,tuple)):
            self.send_message(account.jid, *result)
        else:
            self.send_message(account.jid, result)
    
    def send_message(self, jid, text, html=None):
        if html is not None:
            html_block = (u'<html xmlns="http://jabber.org/protocol/xhtml-im">'
                u'<body xmlns="http://www.w3.org/1999/xhtml">%s</body></html>')
            html = ET.XML(html_block % html)
        self.bot.send_message(mto=jid, mbody=text, mhtml=html)


class TwitterManager(object):
    '''
    Manage the twitter accounts
    '''

    def __init__(self):
        self.accounts = {}
    
    def get_account(self, jid):
        try:
            return self.accounts[jid]
        except KeyError:
            return None

    def get_or_create_account(self, jid):
        account = self.get_account(jid)
        if not account:
            account = TwitterAccount(jid)
            self.accounts[jid] = account
        return account


class TwitterAccount(object):
    '''
    Handles a twitter account for an user (JID) and control the authentication
    '''
    def __init__(self, jid):
        self.jid = jid
        self.verified = False
        self.authenticating = False
        self.api = None
        self._token = None
        self._auth = tweepy.OAuthHandler(
                config.TWEET_APP_CONSUMER_TOKEN,
                config.TWEET_APP_CONSUMER_SECRET)
    
    @property
    def simple_jid(self):
        return str(self.jid).split("/", 1)[0]

    def authenticate(self):
        url = self._auth.get_authorization_url()
        self.authenticating = True
        return url
    
    def verify(self, code):
        try:
            self._token = self._auth.get_access_token(code)
        except tweepy.error.TweepError:
            self.verified = False
            self.authenticating = True
            return False
        self.api = tweepy.API(self._auth)
        self.authenticating = False
        self.verified = True
        return True
    
    def save(self):
        try:
            user = User.objects.get(jid=self.simple_jid)
        except User.DoesNotExist:
            user = User(jid=self.simple_jid)
        user.token = self._token.to_string()
        user.save()
    
    def reload_authentication(self):
        try:
            user = User.objects.get(jid=self.simple_jid)
        except User.DoesNotExist:
            return False
        self._token = tweepy.oauth.OAuthToken.from_string(user.token)
        self._auth.set_access_token(self._token.key, self._token.secret)
        self.api = tweepy.API(self._auth)
        return True

class TwitterCommands(object):
    '''
    Calls commands on API object and returns already formated to answer the user
    '''

    def __init__(self, api):
        self.api = api
    
    @property
    def patterns(self):
        patterns = (
            (r'^timeline$', self.home_timeline),
            (r'^timeline (?P<page>\d+)$', self.home_timeline),
            (r'^tweet (?P<tweet>.*)$', self.update_status),
            (r'^dm @(?P<screen_name>[\w_-]+) (?P<text>.*)$', self.send_direct_message),
        )
        return [ (re.compile(regex), func) for regex, func in patterns ]

    def resolve(self, message):
        for (regex, func) in self.patterns:
            match = regex.match(message.strip())
            if match:
                return func, match.groupdict()

        return self.not_found, {}
    
    def not_found(self):
        return u"Command not found"

    def home_timeline(self, page=1):
        status_list = self.api.home_timeline(page=page)
        result_text = []
        result_html = []
        html = u'<a href="http://twitter.com/{user}">@{user}</a>: {msg}'

        for status in status_list:
            user = status.user.screen_name
            text = status.text
            result_text.append(u'@{0}: {1}'.format(user, text))
            result_html.append(html.format(user=user, msg=text))
         
        return u"\n\n".join(result_text), u"<br/><br/>".join(result_html)
    
    def update_status(self, tweet):
        tweet = tweet.strip()
        
        if not tweet:
            return u"Empty tweet"
        
        if len(tweet) > 140:
            return u"Tweet too long, {0} characters. Must be up to 140.".format(len(tweet))
        self.api.update_status(tweet)

        return u"Tweet sent"

    def send_direct_message(self, screen_name, text):
        try:
            self.api.send_direct_message(screen_name=screen_name, text=text)
        except tweepy.error.TweepError, e:
            return unicode(e.reason)
        
        return u"Message sent"


def main():
    db.connect()
    print("Connected to MongoDB")

    bot = TweetBot(config.BOT_JID, config.BOT_PASSWORD)
    
    bot.registerPlugin('xep_0030')
    bot.registerPlugin('xep_0004')
    bot.registerPlugin('xep_0060')
    bot.registerPlugin('xep_0199')
    
    print("Creating bot")
    
    if bot.connect((config.BOT_HOST, config.BOT_PORT)):
        print("OK")
        bot.process(threaded=False)
        print("\nDone")
    else:
        print("Not connected")



if __name__ == '__main__':
    main()
