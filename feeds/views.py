from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from feeds.feed_handler import FeedHandler

from .models import Feed


@login_required
def index(request):
    feed_list = Feed.objects.order_by('-name')
    context = {'feed_list': feed_list}
    return render(request, 'feeds/index.html', context)


@login_required
def detail(request, feed_id):
    feed = get_object_or_404(Feed, pk=feed_id)
    parsed = FeedHandler(feed.url)
    parsed.process_feed()
    context = dict(
        feed=feed,
        feed_detail=parsed
    )
    return render(request, 'feeds/detail.html', context)


def login_request(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            context = {'error': 'Wrong credintials'}
            return render(request, 'feeds/user-profile.html', {'context': context})
    return render(request, 'feeds/user-profile.html', {})


def user_logout(request):
    logout(request)
    return redirect("index")
