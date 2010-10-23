from mongoengine import Document, StringField

class User(Document):
    '''
    Represents an user connected to twitter using the bot.

    :param jid: client's simple JID, not full, like "user@host.com"
    :param token: oauth token

    '''

    jid = StringField()
    token = StringField()
    
    meta = {
        'collection': 'user_accounts',
    }
    
    def __unicode__(self):
        return u"User: {0}".format(self.jid)
