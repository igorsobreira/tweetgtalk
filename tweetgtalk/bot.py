#!/usr/bin/env python
import sleekxmpp
import tweepy

import config

class TweetBot(sleekxmpp.ClientXMPP):
    
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
    
    def __init__(self, bot=None):
        self.bot = bot
        self.manager = TwitterManager()

    def handle(self, msg):
        body = msg['body'].strip()
        jid = msg.getFrom().jid

        account = self.manager.get_or_create_account(jid)
        if account.verified:
            self.execute_command(account, body)
        else: 
            if account.authenticating:
                if account.verify(body):
                    self.send_message(jid, 'Authentication complete!')
                else:
                    self.send_message(jid, 'Invalid verification code')
            else:
                redirect_url = account.authenticate()
                self.send_message(jid, u'Enter the url bellow and click "Allow"')
                self.send_message(jid, redirect_url)
                self.send_message(jid, u'Enter de verification code:')
    
    def execute_command(self, account, command):
        pass 
    
    def send_message(self, jid, msg):
        self.bot.sendMessage(jid, msg)

class TwitterManager(object):

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

    def __init__(self, jid):
        self.jid = jid
        self.verified = False
        self.authenticating = False
        self._auth = None
        self._api = None

    def authenticate(self):
        self._auth = tweepy.OAuthHandler(
                config.TWEET_APP_CONSUMER_TOKEN,
                config.TWEET_APP_CONSUMER_SECRET)
        url = self._auth.get_authorization_url()
        self.authenticating = True
        return url

    
    def verify(self, code):
        try:
            self._auth.get_access_token(code)
        except tweepy.error.TweepError:
            self.verified = False
            self.authenticating = True
            return False
        self._api = tweepy.API(self._auth)
        self.authenticating = False
        self.verified = True
        return True



def main():
    bot = TweetBot(config.BOT_JID, config.BOT_PASSWORD)
    
    bot.registerPlugin('xep_0030')
    bot.registerPlugin('xep_0004')
    bot.registerPlugin('xep_0060')
    bot.registerPlugin('xep_0199')
    
    print("Created bot")
    
    if bot.connect((config.BOT_HOST, config.BOT_PORT)):
        print("Connected")
        bot.process(threaded=False)
        print("\nDone")
    else:
        print("Not connected")



if __name__ == '__main__':
    main()
