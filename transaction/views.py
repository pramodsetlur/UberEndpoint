# Create your views here.

from twilio.rest import TwilioRestClient
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import MySQLdb
import datetime
from datetime import date, datetime
import pdb
pwd = "scuderia800"

def delete(request):

	if "userid" in request.session:
                id = request.session["userid"]
        else:
                return HttpResponseRedirect("/?n_log=1")

	final_data, heading = [], []

	db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
	cursor = db.cursor()
	sql = "select l.userid, t.position, l.username, t.table_name from Login as l join TableMap as t on l.userid = t.userid where t.table_name in (select table_name from TableMap where userid = %d) order by t.position;" %id
	print "sql:", sql
	cursor.execute(sql)
	table_data = cursor.fetchall()
	db.close()
	if table_data:
		table_name = table_data[0][3]

	deleted = 0
	if request.POST:
		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
		
		cursor = db.cursor()
		sql = "select * from %s where trans_id = %d;" %(table_name, int(request.POST['text-box']))
        	cursor.execute(sql)
        	trans_data = cursor.fetchall()
		if len(trans_data) > 0:
			deleted = "Transaction deleted."
			cursor = db.cursor()
			sql = "delete from %s where trans_id = %d;" %(table_name, int(request.POST['text-box']))
			cursor.execute(sql)
		else:
			deleted = "Transaction ID not found."
		db.commit()
		db.close

	if table_data:

		user_list = ""
		for i in range(len(table_data)):
			user_list += "user" + str(i+1) + ","
		user_list = user_list[:-1]

		db = MySQLdb.connect("localhost","root",pwd,"splitcash")
		cursor = db.cursor()
		sql = "select trans_id, userid, amount, date, comment, %s from %s order by trans_id desc;" % (user_list, table_name)
		print "sql2:", sql
		cursor.execute(sql)
		trans_data = cursor.fetchall()	
		db.close()
	
		names_list = []
		name_dict = {}
		for each in table_data:
			name_dict[int(each[0])] = each[2]
			names_list.append(each[2])

		final_data = []
		for each in trans_data:
			row = [each[0], name_dict[int(each[1])], round(float(each[2]),2), datetime.strptime(str(each[3]), "%Y-%m-%d").strftime("%d %b %Y")] + list(each[5:]) + [each[4]]
			print "row ->", row
			final_data.append(row)

		heading = ["ID", "Name", "Amount", "Date"] + names_list + ["Comment"]
		print "heading:", heading

	
	return render(request, 'transaction/delete.html', {'heading':heading, 'data':final_data, 'deleted':deleted})

def show(request):

	if "userid" in request.session:
                id = request.session["userid"]
        else:
                return HttpResponseRedirect("/?n_log=1")
	
	heading = []
	final_data = []
	db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
	cursor = db.cursor()
	sql = "select l.userid, t.position, l.username, t.table_name from Login as l join TableMap as t on l.userid = t.userid where t.table_name in (select table_name from TableMap where userid = %d) order by t.position;" %id
	print "sql:", sql
	cursor.execute(sql)
	table_data = cursor.fetchall()
	db.close()

	if table_data:
		table_name = table_data[0][3]

		user_list = ""
		for i in range(len(table_data)):
			user_list += "user" + str(i+1) + ","
		user_list = user_list[:-1]

		db = MySQLdb.connect("localhost","root",pwd,"splitcash")
		cursor = db.cursor()
		sql = "select trans_id, userid, amount, date, comment, %s from %s;" % (user_list, table_name)
		print "sql2:", sql
		cursor.execute(sql)
		trans_data = cursor.fetchall()	
		db.close()
	
		names_list = []
		name_dict = {}
		for each in table_data:
			name_dict[int(each[0])] = each[2]
			names_list.append(each[2])

		new_data = []
		for each in trans_data:
			row = [each[0], name_dict[int(each[1])], round(float(each[2]),2), datetime.strptime(str(each[3]), "%Y-%m-%d").strftime("%d %b %Y"), each[4]] + list(each[5:])
			print "row ->", row
			new_data.append(row)

		heading = ["ID", "Name", "Amount", "Date"] + names_list + ["Comment"]
		print "heading:", heading
		
	return render(request, 'transaction/show.html', {'data':final_data})

def add(request):
	if "userid" in request.session:
                id = request.session["userid"]
        else:
                return HttpResponseRedirect("/?n_log=1")
	
	db = MySQLdb.connect("localhost","root",pwd,"splitcash")
	cursor = db.cursor()
	sql = "select t.userid, t.table_name, t.position, l.username, l.email, l.phone from TableMap as t join Login as l on t.userid = l.userid where t.table_name in (select table_name from TableMap where userid = %d) order by t.position;" %int(id)
	cursor.execute(sql)
	user_data = cursor.fetchall()
	db.close()
	if user_data:
		empty = 0
		table_name = str(user_data[0][1])
	else:
		empty = 1
	
	names_dict = {}
	names = []
	for each in user_data:
		names.append({str(each[0]):each[3]})
		names_dict[str(each[0])] = each[3]
	print names

	added = 0
	if request.POST:
		print "request.POST ---->", request.POST
		poster_id = int(request.POST['user'])
		amount = round(float(request.POST['amount']),2) #amount
		
		LHS = ""
		sql_users = ""
		count = 1
		sms_names = ""
		mobile_numbers = []
		adder_number = ""
		for each in user_data:
			if str(each[0]) == request.POST['user']:
				adder_number = str(each[5])
			LHS += "user" + str(count) + ","
			if "c"+str(each[0]) in request.POST:
				sql_users += "1,"
				sms_names += names_dict[str(each[0])] + ", "
				mobile_numbers.append(str(each[5]))
			else:
				sql_users += "0,"
			count += 1
		if adder_number not in mobile_numbers:
			mobile_numbers.append(adder_number)
		print "mobile numbers:", mobile_numbers
		sql_users = sql_users[:-1]
		LHS = LHS[:-1]
		print "sql_users --->", sql_users
		print "LHS --->", LHS
		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
		cursor = db.cursor()
		sql = "insert into %s (userid, amount, date, comment, %s) values ( %d, %10.2f, '%s','%s'," %(table_name, LHS, poster_id, amount, datetime.now().date(), request.POST['comment'])
		sql += sql_users + ")"
		print "sql ---> ", sql
		cursor.execute(sql)
		db.commit()
		db.close
		added = 1

		#send sms
		print "NAMES:", names_dict
		adder = names_dict[str(poster_id)]
		sms_body = " " + adder + " added $" + str(amount) + " to be shared between " + sms_names
		
		sms_body = sms_body[:-2]
		sms_body += ". Comment: " + request.POST['comment']
		print "sms_body:", sms_body
		try:
			account_sid = "AC91b1d7565ef291d5932d9b44710ce283"
			auth_token = "fb8b4e37b614bc5caa43f846af674ddb"
			client = TwilioRestClient(account_sid, auth_token)
			print "MOBILE:", mobile_numbers
			for each in mobile_numbers:
				message = client.messages.create(body=sms_body, to=each, from_="+14242778880")
		except:
			print "SMS not sent!"
	return render(request, 'transaction/add.html', {'names':names, 'empty':empty, 'user_data':user_data, 'added':added})
