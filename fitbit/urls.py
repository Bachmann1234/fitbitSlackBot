from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^fitbitredirect$', views.fitbit_redirect, name='fitbit_redirect'),
    url(r'^postmessage/(?P<weight>(\w|\.)*)/$', views.post_weight_to_slack, name='post_message'),

]