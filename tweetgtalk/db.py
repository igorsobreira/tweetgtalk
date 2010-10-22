import mongoengine

def connect(*args, **kwargs):
    return mongoengine.connect(*args, **kwargs)
