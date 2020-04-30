from datetime import datetime
from time import mktime
import pytz
import feedparser


class FeedHandler:
    RSS_LOGO = 'https://upload.wikimedia.org/wikipedia/commons/4/46/Generic_Feed-icon.svg'

    def __init__(self, url):
        self.url = url
        self.raw_feed = feedparser.parse(url)
        self.subtitle = self.raw_feed['feed'].get('subtitle', '')
        self.logo = self.raw_feed['feed'].get('href', self.RSS_LOGO)
        self.min_pub_date = None
        self.max_pub_date = None
        self.processed_feed = []

    def process_feed(self):
        if not self.processed_feed:
            for entry in self.raw_feed['entries']:
                self.processed_feed.append(FeedArticle(entry))
                if not self.min_pub_date:
                    self.min_pub_date = self.max_pub_date = self.processed_feed[-1].published_at_datetime
                elif self.min_pub_date > self.processed_feed[-1].published_at_datetime:
                    self.min_pub_date = self.processed_feed[-1].published_at_datetime
                elif self.max_pub_date < self.processed_feed[-1].published_at_datetime:
                    self.max_pub_date = self.processed_feed[-1].published_at_datetime

    def refresh_feed(self):
        self.raw_feed = feedparser.parse(self.url)
        self.processed_feed = []
        self.process_feed()


class FeedArticle:
    def __init__(self, article):
        self.title = article['title']
        self.url = article['link']
        self.published_at_datetime = pytz.utc.localize(datetime.fromtimestamp(mktime(article['published_parsed'])))
        self.thumbnail = article['media_thumbnail'][0]['url']
        self.author = article['author']
        self.detail = article['summary']
