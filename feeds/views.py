from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
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
    context = {'request_type': 'login'}
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            context['error'] = {'Wrong credintials'}
            return render(request, 'feeds/user-profile.html', {'context': context})
    return render(request, 'feeds/user-profile.html', {'context': context})


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
    return render(request, 'feeds/user-profile.html', context=context)


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
    return render(request, 'feeds/user-profile.html', context=context)


def user_logout(request):
    logout(request)
    return redirect('index')
