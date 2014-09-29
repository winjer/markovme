
import random
import os
import sys
import codecs
import markovgen
import twitter
import secrets
import stat
import time

api = twitter.Api(consumer_key=secrets.consumer_key,
                  consumer_secret=secrets.consumer_secret,
                  access_token_key=secrets.token,
                  access_token_secret=secrets.secret)

class Stream:

    streams_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "streams")

    def __init__(self, screen_name):
        self.screen_name = screen_name
        self.max_id = self.read_id("max")
        self.new_id = self.read_id("new")

    def stream_file(self):
        return os.path.join(self.streams_dir, self.screen_name)

    def id_file(self, name):
        return os.path.join(self.streams_dir, self.screen_name + "." + name)

    def read_id(self, name):
        id_file = self.id_file(name)
        if not os.path.exists(id_file):
            this_id = None
        else:
            this_id = int(open(id_file).read())
        return this_id

    def recent_id(self, name):
        id_file = self.id_file(name)
        return int(time.time() - os.stat(id_file)[stat.ST_MTIME])

    def write_id(self, name, value):
        id_file = self.id_file(name)
        open(id_file, "w").write(str(value))

    def append_stream(self, lines):
        f = codecs.open(self.stream_file(), "a", encoding="utf-8")
        for l in lines:
            print >> f, l

    def sentence(self):
        f = codecs.open(self.stream_file(), encoding="UTF-8")
        m = markovgen.Markov(f)
        s = m.sentence()
        while len(s) < 20 or len(s) > 130:
            s = m.sentence()
        s = self.correct(s)
        return s

    def correct(self, s):
        # expensive implementation
        replacements = [
            ("@", ""),
            ("(", ","),
            (")", ","),
        ]
        for x, y in replacements:
            s = s.replace(x, y)
        return s

    def tweet(self):
        if os.path.exists(self.stream_file()):
            s = self.sentence()
            text = u"@%s %s" % (self.screen_name, s)
            api.PostUpdate(text)
            return s

    def update(self):
        if self.new_id is not None:
            self.frontfill()
        if self.max_id != -1:
            self.backfill()

    def frontfill(self):
        print "Frontfilling", self.screen_name
        if self.recent_id("new") < 900:
            print "Updated too recently, skipping"
            return
        print "Fetching latest 200 tweets for", self.screen_name
        s = api.GetUserTimeline(screen_name=self.screen_name, count=200, since_id=self.new_id)
        if not s:
            return
        self.new_id = s[0].id
        self.write_id("new", self.new_id)
        self.append_stream([x.text for x in s])

    def backfill(self):
        print "Backfilling", self.screen_name
        if self.max_id is not None:
            if self.recent_id("max") < 900:
                print "Updated too recently, skipping"
                return
        # never more than 5 requests for one user in any one
        # window
        for i in range(0, 5):
            print "Fetching older tweets for", self.screen_name
            try:
                s = api.GetUserTimeline(screen_name=self.screen_name, count=200, max_id=self.max_id)
            except twitter.TwitterError:
                print "Rate limit exceeded"
                return
            if not s:
                break
            if self.new_id == None:
                self.new_id = s[0].id
                self.write_id("new", self.new_id)
            self.append_stream([x.text for x in s])
            self.max_id = s[-1].id
            self.write_id("max", self.max_id)
        self.max_id = -1
        self.write_id("max", self.max_id)


def update_all(followers):
    for u in followers:
        stream = Stream(u.screen_name)
        try:
            stream.update()
        except twitter.TwitterError:
            print "Rate count exceeded, stopping updates"
            return

def tweet_all(followers):
    for u in followers:
        if random.randint(0, 16) == 0:
            stream = Stream(u.screen_name)
            text = stream.tweet()
            print "Tweeted at", u.screen_name, ":", text

def main(argv=()):
    # phase 1, update our follower data
    try:
        followers = api.GetFollowers()
    except twitter.TwitterError:
        print "Follower count rate limited, quitting"
        return
    update_all(followers)
    tweet_all(followers)

def blah():
    name = sys.argv[1]
    f = codecs.open(name, encoding="UTF-8")
    m = markovgen.Markov(f)
    print m.sentence()
