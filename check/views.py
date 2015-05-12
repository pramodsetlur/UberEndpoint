# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import MySQLdb
import datetime
import pdb
pwd = "scuderia800"

def profile(request):
	if "userid" in request.session:
                id = request.session["userid"]
        else:
                return HttpResponseRedirect("/?n_log=1")
	
	invite_data = 0; invited = 0; invite_name = ""
	if request.GET:
		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
		cursor = db.cursor()
		sql = "insert into Invite (userid, receiver_email, accepted) values ('%s','%s',0);" %(id,request.GET["email"])
		cursor.execute(sql)
		db.commit()
		db.close()
		invited = 1

	db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
        cursor = db.cursor()
        sql = "select * from Login where userid = '%s';" %id
        cursor.execute(sql)
        trans_data = cursor.fetchall()
        db.close()
	
	name = trans_data[0][1]
	email = trans_data[0][3]
	phone = trans_data[0][4]

	if request.POST:
		print "accepting this guy's request => ", request.POST["invite_id"]
		print "I am: ", name
		inviting_id = request.POST["invite_id"]
		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
	        cursor = db.cursor()
        	sql = "select * from TableMap where userid = '%s';" %inviting_id
        	cursor.execute(sql)
		table_map = cursor.fetchall()
		db.close()

		if table_map:
			# Add user to existing table
			table_name = table_map[0][1]
			print "table map", table_name
			db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
                        
			cursor = db.cursor()
                        sql = "select count from TableCount where table_name = '%s';" %table_name
                        print sql
                        cursor.execute(sql)
			count = cursor.fetchall()
			count = int(count[0][0])
				
			cursor = db.cursor()
                        sql = "alter table %s add column (user" %table_name 
			sql += str(count+1) + " integer);" 
                        print sql
                        cursor.execute(sql)

			cursor = db.cursor()
                        sql = "insert into TableMap (userid, table_name, position) values (%d,'%s',%d)" %(int(id),table_name,count+1)
                        print sql
                        cursor.execute(sql)

			cursor = db.cursor()
                        sql = "update Invite set accepted = 1 where userid = %d and receiver_email = '%s'" %(int(inviting_id),email)
                        print sql
                        cursor.execute(sql)

                        cursor = db.cursor()
                        sql = "update TableCount set count = count + 1 where table_name ='%s';" %table_name
                        print sql
                        cursor.execute(sql)
			db.commit()
			db.close()

		else:
			# Generate new table name
			table_name = "Transactions" + str(inviting_id) 
			print "new table name", table_name
			db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
			cursor = db.cursor()
			sql = "create table %s (trans_id int auto_increment, userid int, amount decimal(10,2), date date, comment varchar(1000), user1 int, user2 int, primary key (trans_id));" %table_name
			print sql
			cursor.execute(sql)

			cursor = db.cursor()
			sql = "insert into TableMap (userid, table_name, position) values (%d,'%s',1)" %(int(inviting_id),table_name)
			print sql
			cursor.execute(sql)

			cursor = db.cursor()
                        sql = "insert into TableMap (userid, table_name, position) values (%d,'%s',2)" %(int(id),table_name)
                        print sql
			cursor.execute(sql)

                        cursor = db.cursor()
                        sql = "update Invite set accepted = 1 where userid = %d and receiver_email = '%s'" %(int(inviting_id),email)
                        print sql
                        cursor.execute(sql)

			cursor = db.cursor()
                        sql = "insert into TableCount (table_name, count) values ('%s',2)" %table_name
                        print sql
                        cursor.execute(sql)

			db.commit()
			db.close()
	
	db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
        cursor = db.cursor()
        sql = "select * from Invite where receiver_email = '%s' and accepted = 0;" %trans_data[0][3]
        cursor.execute(sql)
        invite_data = cursor.fetchall()
	if invite_data:
		invite_data = invite_data[0][0]
		cursor = db.cursor()
		sql = "select username from Login where userid = '%s';" %invite_data
		cursor.execute(sql)
		invite_name = cursor.fetchall()
		invite_name = invite_name[0][0]
        db.close()

	return render(request, 'check/profile.html', {'invite_name':invite_name, 'invite_userid':invite_data, 'invited':invited, 'name':name, 'email':email, 'phone':phone})

def status(request):
	if "userid" in request.session:
		id = request.session["userid"]
	else:
		return HttpResponseRedirect("/?n_log=1")

	# New method starts here

	final_data = []

	db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
        cursor = db.cursor()
        sql = "select table_name from TableMap where userid = %d;" %id
        cursor.execute(sql)
        table_name = cursor.fetchall()
        
	if table_name:
		table_name = table_name[0][0]
				
		cursor = db.cursor()
		sql = "select userid, position from TableMap where table_name = '%s' order by position;" %table_name
		cursor.execute(sql)
		mapping = cursor.fetchall()
		pos_mapping = {}
		for each in mapping:
			pos_mapping[int(each[0])] = int(each[1])
		
		dues_size = len(mapping)
		
		users = ""
		for i in range(dues_size):
			users += "user" + str(i+1) + ","
		users = users[:-1]
		cursor = db.cursor()
		sql = "select userid, amount, " + users
		sql += " from %s;" %table_name
		cursor.execute(sql)
		table_data = cursor.fetchall()
		
		dues_data = []
		for each in table_data:
			dues_data.append([pos_mapping[int(each[0])],float(each[1])]+[each[2:]])
		
		# creating the dues matrix
		dues = []
		for i in range(dues_size):
			dues.append([0]*dues_size)

		# adding each transaction to dues matrix
		for each in dues_data:
			adder = int(each[0])
			amount_added = float(each[1])
			ones = list(each[2])
			count_ones = ones.count(1)
			div_amount = amount_added / count_ones
			for i in range(len(ones)):
				if ones[i] and i != adder-1:
					dues[i][adder-1] += div_amount
		
		for each in dues:
			print each
		# eliminates 1 on 1 dues
		i = 0
		while i < len(dues):
			j = 0
			while j < len(dues):
				if dues[i][j] and dues[j][i]:
					if dues[i][j] >= dues[j][i]:
						dues[i][j] -= dues[j][i]
						if round(dues[i][j],1) == 0:
							dues[i][j] = 0
						dues[j][i] = 0
					else:
						dues[j][i] -= dues[i][j]
						if round(dues[j][i],1) == 0:
							dues[j][i] = 0
						dues[i][j] = 0
				j += 1
			i += 1

		# eliminates cycles
		i = 0
		while i < len(dues):
			j = 0
			while j < len(dues):
				if dues[i][j]:
					for k in range(len(dues)):
						if dues[j][k]:
							if i == k:
								if round(dues[i][j] - dues[j][k],1) == 0:
									dues[i][j], dues[j][k] = 0, 0
								elif dues[i][j] > dues[j][k]:
									dues[i][j] -= dues[j][k]
									dues[j][k] = 0
								else:
									dues[j][k] -= dues[i][j]
									dues[i][j] = 0

							elif dues[j][k] >= dues[i][j]:
								dues[i][k] += dues[i][j]
								dues[j][k] -= dues[i][j]
								if round(dues[j][k],1) == 0:
									dues[j][k] = 0
								dues[i][j] = 0

							else:
								dues[i][k] += dues[j][k]
								dues[i][j] -= dues[j][k]
								if round(dues[i][j],1) == 0:
									dues[i][j] = 0
								dues[j][k] = 0
							i = 0; j = 0; break
				j += 1
			i += 1

		db = MySQLdb.connect("localhost","root",pwd,"splitcash" )
        	cursor = db.cursor()
        	sql = "select t.position, l.username from TableMap as t join Login as l on t.userid = l.userid and t.table_name = '%s';" %table_name
        	cursor.execute(sql)
		name_data = cursor.fetchall()
		db.close()
		
		name_dict = {}
		for each in name_data:
			name_dict[int(each[0])] = each[1]
		print "name_dict", name_dict

		i = 0
		while i<len(dues):
			j = 0
			while j<len(dues):
				if dues[i][j]:
					row = name_dict[i+1] + " owes " + name_dict[j+1] + " $ " + str(round(dues[i][j],2))
					final_data.append(row)
				j += 1
			i += 1	

	return render(request, 'check/status.html', {'final_data':final_data})
