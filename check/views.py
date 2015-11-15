# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import datetime
import pdb

def status(request):
	from rauth import OAuth2Service

	uber_api = OAuth2Service(
	     client_id='9x5d54-oGBfVr-3zC4wAnYyY9783iF9k',
	     client_secret='iREizzW6dqHtqdCZFIjbWTQYxTwiEUdKQxV7Hta',
	     name='Findango',
	     authorize_url='https://login.uber.com/oauth/authorize',
	     access_token_url='https://login.uber.com/oauth/token',
	     base_url='https://api.uber.com/v1/',
	 )

	parameters = {
	    'response_type': 'code',
	    'redirect_uri': 'http://54.218.55.51/check/',
	    'scope': 'profile',
	}

	# Redirect user here to authorize your application
	login_url = uber_api.get_authorize_url(**parameters)
	return render(request, 'check/status.html', {'final_data':login_url})
