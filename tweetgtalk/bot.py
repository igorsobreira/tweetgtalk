#!/usr/bin/env python
import sleekxmpp
import tweepy

import config

class TweetBot(sleekxmpp.ClientXMPP):
    
    def __init__(self, jid, password):
        super(TweetBot, self).__init__(jid, password)
        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)
        
        self.twitter = TwitterManager()

    def on_start(self, event):
        self.sendPresence()

    def on_message(self, msg):
        if msg['type'] == 'chat' and msg['body']:
            self.handle_message(msg)

    def handle_message(self, msg):
        body = msg['body'].strip()

        if self.twitter.waiting_permission:
            self.twitter.create_api(verifier=body)
            self.sendMessage(msg.getFrom(), 'Authentication complete!')
            self.sendMessage(msg.getFrom(), str(self.twitter.api.home_timeline()))

        elif body == 'start':
            redirect_url = self.twitter.authenticate()
            self.sendMessage(msg.getFrom(), redirect_url)
            self.sendMessage(msg.getFrom(), 'Enter de verifier bellow:')



class TwitterManager(object):

    def __init__(self):
        self.auth = None
        self.api = None
        self.waiting_permission = False

    def authenticate(self):
        self.auth = tweepy.OAuthHandler(
                config.TWEET_APP_CONSUMER_TOKEN,
                config.TWEET_APP_CONSUMER_SECRET)
        redirect_url = self.auth.get_authorization_url()
        self.waiting_permission = True
        return redirect_url
    
    def create_api(self, verifier):
        self.auth.get_access_token(verifier)
        self.api = tweepy.API(self.auth)
    

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
