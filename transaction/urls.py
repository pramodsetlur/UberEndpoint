from django.conf.urls import patterns, url

from transaction import views

urlpatterns = patterns('',
		    url(r'^show/', views.show, name='show'),
		    url(r'^add/', views.add, name='add'),
		    url(r'^delete/', views.delete, name='delete'),
		    )
