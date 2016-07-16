from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^fitbitredirect$', views.fitbit_redirect, name='fitbit_redirect'),
    url(r'^postmessage$', views.post_weight_to_slack, name='post_message'),
    url(r'^postmessagediscord$', views.post_weight_to_discord, name='post_message_discord'),
]
