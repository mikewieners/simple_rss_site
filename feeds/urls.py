from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<feed_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^login/$', views.login_request, name='login'),
    url(r"^logout/$", views.user_logout, name='logout'),
    url(r'^register/$', views.register_user, name='register'),
    url(r'^user-profile/$', views.user_profile, name='user_profile'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^preview/$', views.feed_preview, name='preview')
]
