from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User

from feeds.feed_handler import FeedHandler

from .models import Feed


@login_required
def index(request):
    feed_list = Feed.objects.filter(subscribers=request.user.id).order_by('-name')
    context = {'feed_list': feed_list}
    return render(request, 'feeds/feed-list.html', context)


@login_required
def subscribe(request, context={'request_type': 'subscribe'}):
    if request.method == 'GET':
        feed_list = Feed.objects.exclude(subscribers=request.user.id)
        context['feed_list'] = feed_list
        return render(request, 'feeds/feed-list.html', context)
    if request.method == 'POST':
        if request.POST.get('url'):
            feed_url = request.POST.get('url')
            request.session['_pending_subscription'] = feed_url
            # TODO: Validate URL and check for duplicates in database
            # return detail(request, feed_url=feed_url, context=context)
            return redirect('/feeds/preview/')
        if request.session.get('pending_subscription'):
            return


@login_required
def feed_preview(request):
    feed_url = request.session.get('_pending_subscription')
    parsed = FeedHandler(feed_url)
    parsed.process_feed()
    if request.method == 'GET':
        context = dict(
            feed_detail=parsed,
            request_type='subscribe'
        )
        return render(request, 'feeds/feed-detail.html', context)
    if request.method == 'POST':
        feed = Feed.objects.create(
            url=parsed.url,
            name=parsed.title,
            subtitle=parsed.subtitle,
            logo=parsed.logo
        )
        feed.subscribers.add(request.user)
        request.session.pop('_pending_subscription')
        return redirect('/feeds/')


@login_required
def detail(request, feed_id, context={}):
    feed = get_object_or_404(Feed, pk=feed_id)
    if request.method == 'POST':
        feed.subscribers.add(request.user)
        context.pop('request_type')
        return redirect('/feeds/')
    feed_url = feed.url
    context['feed'] = feed
    parsed = FeedHandler(feed_url)
    parsed.process_feed()
    context['feed_detail'] = parsed
    if request.user.id not in [user.get('id') for user in feed.subscribers.values()]:
        context['request_type'] = 'subscribe'
    return render(request, 'feeds/feed-detail.html', context)


def login_request(request):
    if request.user.is_authenticated:
        return redirect("index")
    context = {'request_type': 'login'}
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("index")
            else:
                context['error'] = {'Wrong credintials'}
                return render(request, 'feeds/user-profile.html', {'context': context})
        context['error_message'] = form.errors
    return render(request, 'feeds/user-profile.html', context)


def register_user(request):
    context = {}
    if request.user.is_authenticated:
        return user_profile(request)
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get('password1')
            username = form.cleaned_data.get('username')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('index')
        context['error_message'] = str(form.errors)
    context['request_type'] = 'register_user'
    return render(request, 'feeds/user-profile.html', context)


@login_required
def user_profile(request):
    context = {}
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
        return redirect('user_profile')
    context['request_type'] = 'change_password'
    return render(request, 'feeds/user-profile.html', context)


def user_logout(request):
    logout(request)
    return redirect('index')
