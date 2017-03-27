from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^read/', views.show_consumed_message, name='read consumed messages'),
    url(r'^$', views.start_consumer, name='start consumer'),
]