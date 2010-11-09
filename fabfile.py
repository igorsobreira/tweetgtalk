from fabric.api import *
from tweetgtalk import config

env.hosts = [config.SSH_HOST]

root = config.PROJECT_ROOT

def start():
    with cd(root):
        run("screen -d -m  ../bin/python tweetgtalk/bot.py >tweetgtalk.log 2>&1")

def stop():
    pids = run("ps aux | grep tweetgtalk/bot.py | grep -v grep | awk '{print $2}'")
    run('kill -15 %s' % ' '.join(pids.split('\n')))

def update():
    with cd(root):
        run('git pull origin master')
