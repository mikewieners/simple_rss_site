from datetime import datetime
from time import mktime
import pytz
import feedparser
from html.parser import HTMLParser


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
                article = FeedArticle(entry)
                article.parse_detail()
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
        self.title = article.get('title')
        self.url = article.get('link')
        self.published_at_datetime = pytz.utc.localize(datetime.fromtimestamp(mktime(article['published_parsed'])))
        self.author = article.get('author', 'Not Listed')
        self.detail = article['summary'].strip('\n')
        self.thumbnail = None
        self.summary = None

    def parse_detail(self):
        parsed_detail = ParseDetail().feed(self.detail)
        self.summary = self.detail[parsed_detail[0]:parsed_detail[1]]
        self.thumbnail = f'<img src="{parsed_detail.image}" class="article_thumbnail">' if parsed_detail.image else self.thumbnail


class ParseDetail(HTMLParser):
    image = None
    content_range = [0, 0]
    finished = False

    def handle_starttag(self, tag, attrs):
        if self.image and self.content_range[0] == 0:
            self.content_range[0] = self.getpos()[1]
        if tag == 'img':
            if not self.image:
                for attr in attrs:
                    if attr[0] == 'src':
                        self.image = attr[1]
            else:
                self.finished = True
        elif tag != 'p':
            self.finished = True

    def handle_endtag(self, tag):
        if not self.finished:
            self.content_range[1] = self.getpos()[1] + len(tag) + 3
