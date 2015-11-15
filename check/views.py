# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import datetime
import pdb

def status(request):
	return render(request, 'check/status.html', {'final_data':"Hello World"})
