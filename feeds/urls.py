from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<feed_id>[0-9]+)/$', views.detail, name='detail'),
    url('login/', views.login_request, name='login'),
    url(r"^logout/$", views.user_logout, name='logout'),
]
