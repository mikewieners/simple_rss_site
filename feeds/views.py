from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from feeds.feed_handler import FeedHandler

from .models import Feed


def index(request):
    feed_list = Feed.objects.order_by('-name')
    context = {'feed_list': feed_list}
    return render(request, 'feeds/index.html', context)


def detail(request, feed_id):
    feed = get_object_or_404(Feed, pk=feed_id)
    parsed = FeedHandler(feed.url)
    parsed.process_feed()
    context = dict(
        feed=feed,
        feed_detail=parsed
    )
    return render(request, 'feeds/detail.html', context)
