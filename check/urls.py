from django.conf.urls import patterns, url

from check import views

urlpatterns = patterns('',
	url(r'^$', views.status, name='status'),
)
