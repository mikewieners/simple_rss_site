from datetime import datetime
from time import mktime
import pytz
import feedparser
import re
from html.parser import HTMLParser


class FeedHandler:

    def __init__(self, url):
        self.raw_feed = feedparser.parse(url)
        self.url = url
        self.title = self.raw_feed['feed'].get('title', self.url)
        self.subtitle = self.raw_feed['feed'].get('subtitle', '')
        self.logo = None
        self.article_count = 0
        self.thumbnail_count = 0
        self.min_pub_date = None
        self.max_pub_date = None
        self.processed_feed = []

    def process_feed(self):
        if self.raw_feed['feed'].get('image'):
            self.logo = self.raw_feed['feed']['image'].get('href')
        if not self.processed_feed:
            for entry in self.raw_feed['entries']:
                article = FeedArticle(entry)
                article.parse_detail()
                self.processed_feed.append(article)
                if not self.min_pub_date:
                    self.min_pub_date = self.max_pub_date = self.processed_feed[-1].published_at_datetime
                elif self.min_pub_date > self.processed_feed[-1].published_at_datetime:
                    self.min_pub_date = self.processed_feed[-1].published_at_datetime
                elif self.max_pub_date < self.processed_feed[-1].published_at_datetime:
                    self.max_pub_date = self.processed_feed[-1].published_at_datetime
                self.thumbnail_count += 1 if article.thumbnail else self.thumbnail_count
            self.article_count = len(self.processed_feed)

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
        self.detail = article['summary'].replace('\n', '')
        self.thumbnail = None
        self.summary = None

    def parse_detail(self):
        parser = ParseDetail()
        parser.feed(self.detail)
        if parser.content_range[1] == 0:
            self.summary = f'<p>{self.detail}</p>'
        else:
            self.summary = self.detail[parser.content_range[0]:parser.content_range[1]]
            self.thumbnail = f'<img src="{parser.image}" class="article-thumbnail">' if parser.image else self.thumbnail


class ParseDetail(HTMLParser):
    image = None
    content_range = [0, 0]
    finished = False
    update_start_of_range = False

    def handle_starttag(self, tag, attrs):
        if self.update_start_of_range:
            self.content_range[0] = self.getpos()[1]
            self.update_start_of_range = False
        if tag == 'img':
            if not self.image:
                for attr in attrs:
                    if attr[0] == 'src':
                        self.image = attr[1]
                self.update_start_of_range = True
            else:
                self.finished = True
        # elif tag not in ['p', 'a', 'em', 'strong', 'div']:
        elif re.match('h[1-6]', tag):
            self.finished = True

    def handle_endtag(self, tag):
        if not self.finished:
            self.content_range[1] = self.getpos()[1] + len(tag) + 3
