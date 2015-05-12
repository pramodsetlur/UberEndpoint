# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import MySQLdb
import os
import hashlib
pwd = "scuderia800"
from django.contrib.auth.hashers import check_password, make_password

def login(request):

	print "REQUEST: ", request

	if "userid" in request.session:
        	return HttpResponseRedirect("/check/")        
	
	reg = 0; inc = 0; n_log = 0
	if request.GET:
		if "reg" in request.GET:
        		reg = 1
		if "n_log" in request.GET:
			n_log = 1
	if request.POST:
		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
                cursor = db.cursor()
		#password = make_password(request.POST['Password'], salt=None, hasher="sha1")
		password = request.POST['Password']
                sql = "select userid, password from Login where email = '%s'" %(request.POST['Email'])
		cursor.execute(sql)
                login_data = cursor.fetchall()
                db.close
		if login_data and check_password(password, login_data[0][1]):
			request.session["userid"] = login_data[0][0]
			return HttpResponseRedirect("/check")
		else:
			inc = 1

	return render(request, 'login/login.html', {'reg': reg, 'inc': inc, 'n_log': n_log})
	#return HttpResponseRedirect("/check")

def register(request):
	registered = 0; mismatch = 0; empty = 0; name = ""; email = ""; phone = ""
	if request.POST:
		name = request.POST['Name']
		email = request.POST['Email']
		phone = request.POST['Phone']
		if request.POST['Password1'] == request.POST['Password2']:
			if request.POST['Password1'] == "":
				empty = 1
			else:
				db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
				cursor = db.cursor()
				password = make_password(request.POST['Password1'], salt=None, hasher="md5")
				
				sql = "insert into Login (username, password, email, phone) values ('%s', '%s', '%s', '%s');" %(name,password,email,phone)
				print "SQL -----> ", sql
				cursor.execute(sql)
				db.commit();
				db.close()
				registered = 1
				return HttpResponseRedirect('/?reg=1')
		else:
			mismatch = 1
	return render(request, 'login/register.html', {'empty':empty, 'mismatch':mismatch, 'name':name, 'email':email, 'phone':phone})

def logout(request):
	if "userid" in request.session:
		del request.session["userid"]
	return HttpResponseRedirect('/?log_out=1')
