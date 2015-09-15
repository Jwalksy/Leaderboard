from flask import Flask, render_template
import datetime
import svn.remote
import logging
import parser
import psycopg2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import uuid
import json

app = Flask('LeaderboardFinal')

# Psycopg2 database connection
CONN = psycopg2.connect('dbname=annachi user=annachi host=localhost')
CUR = CONN.cursor()

# check if the a customerID table exists already, if not create a new table
CUR.execute("select exists(select * from information_schema.tables where table_name=%s)", ('customerid',))
z = CUR.fetchone()[0]

if not z:
	# print "hello"
	CUR.execute("CREATE TABLE customerid(user_name varchar, customer_id varchar);")
	CONN.commit()

CUR.execute("select exists(select * from information_schema.columns where table_name='customerid')", ('row_num',))
p = CUR.fetchone()[0]
if not p:
	CUR.execute("ALTER TABLE customerid ADD COLUMN row_num BIGSERIAL PRIMARY KEY;")
	CONN.commit()

# check if the table exists already, if not create a new table
CUR.execute("select exists(select * from information_schema.tables where table_name=%s)", ('spicerack',))
x = CUR.fetchone()[0]
# print x
if not x:
	# print "hello"
	CUR.execute("CREATE TABLE spicerack (user_name varchar, homework varchar, test_name varchar, execution_time varchar, submission_number varchar, core_count int, last_update timestamp without time zone DEFAULT now());")
	CONN.commit()

CUR.execute("select exists(select * from information_schema.columns where table_name='spicerack')", ('row_num',))
y = CUR.fetchone()[0]
if not y:
	CUR.execute("ALTER TABLE spicerack ADD COLUMN row_num BIGSERIAL PRIMARY KEY;")
	CONN.commit()



# Pages

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/error.html')
def error():
	return render_template('error.html')

@app.route('/line.html')
def lineplots():

	# fetch all test names
	CUR.execute("SELECT DISTINCT test_name FROM spicerack")
	test_names = CUR.fetchall()
	
	# fetch all core counts
	CUR.execute("SELECT DISTINCT core_count FROM spicerack")
	core_counts = CUR.fetchall()

	plotdatas=[]

	for test in test_names:
		exec_time=[]
		core_list=[]
		for core in core_counts:
			CUR.execute("select exists(select * from spicerack where test_name = %s and core_count = %s and user_name= %s)",(test, core,'anna'))
			exists = CUR.fetchone()[0]
			if exists:
				CUR.execute("SELECT * FROM spicerack WHERE test_name = %s and core_count = %s and user_name= %s",(test, core,'anna'))
				strtime=CUR.fetchone()[3]
				single_time=int(strtime)
				exec_time.append(single_time)
				core_list.append(int(core[0]))
			else:
				print "no data entry in db",(test, '9','anna',)
				return render_template('error.html', errormessage='no request data in db', info=[test,core,'anna'])
		data=zip(core_list,exec_time)
		data.sort()
		plotdata=[]
		for i in range(len(data)):
			plotdata.append([data[i][0],data[i][1]])
		plotdatas.append(plotdata)

	return render_template('line.html', plotdatas=plotdatas, student='student '+'143')


@app.route('/charts.html',methods = ['GET'])
def charts():
	# fetch all test names
	CUR.execute("SELECT DISTINCT test_name FROM spicerack")
	test_names = CUR.fetchall()
	
	# fetch all core counts
	CUR.execute("SELECT DISTINCT core_count FROM spicerack")
	core_counts = CUR.fetchall()

	bardata=[]
	# label is the test name and core count associting with a execution time
	label=[]

	# interval on the x-axis on the bar graph
	interval=1000

	# for each test and core, fetch all the execution times and find the distribution
	for test in test_names:
		for core in core_counts:
			CUR.execute("SELECT execution_time FROM spicerack WHERE test_name = %s and core_count = %s", (test,core))
			exetimelist=CUR.fetchall()
			first=0
			second=0
			third=0
			fourth=0
			fifth=0
			sixth=0
			seventh=0
			eighth=0
			ninth=0
			tenth=0
			# find which interval the exection time belongs to
			for eachtime in exetimelist:
				value=int(eachtime[0])
				if value<interval:
					first+=1
				if value>=interval and value<2*interval:
					second+=1
				if value>=2*interval and value<3*interval:
					third+=1
				if value>=3*interval and value<4*interval:
					fourth+=1
				if value>=4*interval and value<5*interval:
					fifth+=1
				if value>=5*interval and value<6*interval:
					sixth+=1
				if value>=6*interval and value<7*interval:
					seventh+=1
				if value>=7*interval and value<8*interval:
					eighth+=1
				if value>=8*interval and value<9*interval:
					ninth+=1
				if value>=9*interval:
					tenth+=1
			bardata.append([first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth])
			label.append([int(test[0][4]),core[0]])
			# print 'BARDATA',bardata
			# print 'LABEL',label
			# break

	# the number of the bar graphs is going to be generated
	totalgraphs=len(test_names) * len(core_counts)

	return render_template('charts.html', bardata=bardata, totalgraphs=totalgraphs, label=label)

@app.route('/dashboard.html')
def dashboard():
	return render_template('dashboard.html')

@app.route('/blank.html')
def blank():
	return render_template('blank.html')

@app.route('/login.html')
def login():
	return render_template('login.html')

@app.route('/tables.html', methods = ['GET'])
def show_table():
	
	print "hello"
	CUR.execute("SELECT * FROM spicerack;")
	allstu = CUR.fetchall()
	students = [dict(user_name=row[0], test_name = row[2], execution_time = row[3], submission_number = row[4], core_count = row[5], last_update = row[6]) for row in allstu]

    # fetch student customerID and add it to the students
	for stu in students:
		net=stu['user_name']
		CUR.execute("SELECT * FROM customerid WHERE user_name = %s",(net,))
		customerID=CUR.fetchone()[1]
		stu['customernum']=customerID

	return render_template('tables.html', students=students)

# @app.route('/')
# def show_students():
# 	t = CUR.execute("select * from information_schema.columns where table_name='spicerack')", ('test_name', 'execution_time', 'core_count', 'submission_number', 'last_update'))
# 	print t
# 	students = [dict(test_name = row[0], execution_time = row[1], core_count = row[2], submission_number = row[3], last_update = row[4]) for row in CUR.fetchall()]
# 	return render_template('index.html', students = students)

# (user_name, homework, test_name, execution_time, submission_number, core_count, last_update)
# /new_run/<netID>/<runID>

@app.route('/new_run/<netID>/<runID>', methods = ['POST'])
def new_run(netID, runID):
	"""
	Gets netID and runID and creates a new entry into the database
	"""
	# Receive information from svn update
	netID = str(netID)
	runID = str(runID)
	# parse the data from the file in svn
	# print netID, runID

	submiss = parser.get_test_scores(netID, runID)
	hw = submiss[0]
	scores = submiss[1]
	# print 'SCORES', scores
	for test in scores:
		for ext in scores[test]:
			# add all test scores for this student to the database
			execute = ext[0]
			cores = ext[1]
			date = datetime.datetime.utcnow()
			date = date.strftime('%m/%d/%Y %H:%M:%S')
			CUR.execute("INSERT INTO spicerack (user_name, homework, test_name, execution_time, submission_number, core_count, last_update) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');".format(netID, hw, test, execute, runID, cores, date))
			CONN.commit()
	return render_template('index.html')

# Error log output
logging.basicConfig(filename = 'error.log', level = logging.DEBUG)

# Run app
if __name__ == '__main__':
	# print "name = main"
	app.run()




