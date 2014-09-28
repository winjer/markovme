import sys
import twitter
import secrets
import codecs

api = twitter.Api(consumer_key=secrets.consumer_key,
                  consumer_secret=secrets.consumer_secret,
                  access_token_key=secrets.access_token_key,
                  access_token_secret=secrets.access_token_secret)

def fetch(screen_name):
    f = codecs.open(screen_name, "w", encoding="UTF-8")
    max_id = None
    while True:
        s = api.GetUserTimeline(screen_name=screen_name, max_id=max_id)
        if not s:
            break
        f.writelines([x.text + "\n" for x in s])
        max_id = s[-1].id

if __name__ == "__main__":
    fetch(sys.argv[1])
