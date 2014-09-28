
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

    def backfill(self):
        print "Backfilling", self.screen_name
        if self.max_id == "-1":
            print "No need to backfill, we're done"
            return
        if self.max_id is not None:
            if self.recent_id("max") < 900:
                print "Updated too recently, skipping"
                return
        while True:
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

def main(argv=()):
    # phase 1, update our follower data
    followers = api.GetFollowers()
    for u in followers:
        stream = Stream(u.screen_name)
        stream.backfill()

def blah():
    name = sys.argv[1]
    f = codecs.open(name, encoding="UTF-8")
    m = markovgen.Markov(f)
    print m.sentence()
