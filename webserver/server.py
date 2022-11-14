#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "super secret key"


# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "cl4294"
DB_PASSWORD = "6981"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT * FROM station")
  stations = []
  for result in cursor:
    stations.append(result[1])
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)
  context = dict(data = stations)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")

@app.route('/selection')
def selection():
  uid = [session.get('user_id', None)]
  print("session uid is", uid)
  context = dict(data = uid)
  return render_template("selection.html", **context)

@app.route('/user_entries')
def user_entries():
  return render_template("user_entries.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  #cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  cmd = 'INSERT INTO test(name) VALUES (:name1)';
  g.conn.execute(text(cmd), name1 = name);
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

@app.route('/user_login', methods=['POST'])
def user_login():
	input_name = request.form['username']
	user_addr = request.form['user_addr']
	print(input_name)
	#print("addr below")
	print(user_addr)
	cursor = g.conn.execute('SELECT * FROM app_user')
	#g.conn.execute(text(cmd), i_name = input_name)
	#cursor = g.conn.execute("SELECT * FROM station")
	user_id = -1
	next_id = 1
	for result in cursor:
		next_id += 1
		if result[2] == input_name:
			user_id = result[0]
	cursor.close()
	print("uid is", user_id)
	if user_id == -1 and user_addr == "":
		flash('You are a first-time user. Please fill out the train station closest to you!')
		return redirect('/')
	elif user_id == -1 and user_addr != "":
		cmd = 'INSERT INTO app_user(user_id, closest_station, name) VALUES (:id, :closest_station, :name)'
		g.conn.execute(text(cmd), id=next_id, closest_station=user_addr, name=input_name)
		session['user_id'] = next_id
		session['user_name'] = input_name
		context = dict(data = input_name)
		return render_template("selection.html", **context)
	elif user_id != -1:
		session['user_name'] = input_name
		session['user_id'] = user_id
		#print("session id is ", session['user_id'])
		context = dict(data = input_name)
		return render_template("selection.html", **context)
    
@app.route('/view_saved_entries', methods=['POST'])
def view_saved_entries():
	print("Enter the function")
	uid = session.get('user_id', None)
	print("session uid is", uid)
	cursor = g.conn.execute("SELECT * FROM lists")
	location_ids = []
	for result in cursor:
		if result[0] == session['user_id']:
			location_ids.append(result[1])
	cursor.close()
	cursor = g.conn.execute("SELECT * FROM location")
	locations = []
	for result in cursor:
		if result[0] in location_ids:
			locations.append(result)
	cursor.close()
	print("locations line 263", locations)
	cursor2 = g.conn.execute("SELECT * FROM locates")
	tmp_outputs = []
	for result in cursor2:
		#print("line 267", locations[l])
		for l in range(len(locations)):
			print("l[0], result[0]", (locations[l][0], result[0]))
			if locations[l][0] == result[0]:
				tmp_outputs.append((locations[l][2], locations[l][1], locations[l][3], result[1]))
	
	cursor2.close()
	print("tmp_outputs line 271", tmp_outputs)
	# cursor2 = g.conn.execute("SELECT * FROM locates")
	# tmp_outputs = []
	# for l in locations:
  	# 	for result in cursor2:
	# 		if l[0] == result[0]:
	# 			tmp_outputs.append((l[2], l[1], l[3], result[1]))
    # cursor2.close()

	# # get station name with station id
	outputs = []
	cursor = g.conn.execute("SELECT * from station")
	for t in tmp_outputs:
		for result in cursor:
			if result[0] == t[3]:
				outputs.append((t[0], t[1], t[2], result[1]))
	cursor.close()
	print("outputs line 288", outputs)
	context = dict(data = outputs)
	return render_template("user_entries.html", **context)

@app.route('/go_back', methods=['POST'])
def go_back():
	context = dict(data = session['user_name'])
	return render_template("selection.html", **context)

@app.route('/input', methods=['POST'])
def input():
	context = dict(data = session['user_name'])
	return render_template("location_info.html", **context)

@app.route('/save_location', methods=["POST"])
def save_location():
	l_type = request.form['location_type']
	l_addr = request.form['location_addr']
	business_hour = request.form['business_hour']

	cursor = g.conn.execute("SELECT * FROM location")
	location_ids = []
	ignore_entry = False
	location_id = -1
	for result in cursor:
		if result[2] == l_addr:
			ignore_entry = True
			location_id = result[0]
		location_ids.append(result[0])
	new_id = max(location_ids) + 1
	cursor.close()

	if ignore_entry == False:
		cmd = 'INSERT INTO location(location_id, location_type, address, business_hour) VALUES (:l_id, :l_type, :l_addr, :business_hour)'
		#cmd_cont = 'VALUES (:l_id, :l_type, :l_addr, :business_hour, :visited, :rating, :review)'
		g.conn.execute(text(cmd), l_id=new_id, l_type=l_type, l_addr=l_addr, business_hour=business_hour)
		location_id = new_id

	cmd2 = 'INSERT INTO lists(user_id, location_id, rating) VALUES (:u_id, :l_id, :rating)'
	uid = session.get('user_id', None)
	rating = request.form['rating']
	#rating = -1.0
	if rating == "None":
		rating = None
	g.conn.execute(text(cmd2), u_id=uid, l_id=location_id, rating=rating) #TODO: check duplicate?
	session['location_id'] = location_id
	session['location_addr'] = l_addr
	session['location_type'] = l_type
	session['business_hour'] = business_hour
	context = dict(data = session['user_name'])
	return render_template("transportation_info.html", **context)

@app.route('/save_station', methods=["POST"])
def save_station():
	station_addr = request.form['station_addr']
	route_id = request.form['route_id']
	train_id = request.form['train_id']
	
	cursor = g.conn.execute("SELECT * FROM station")
	add_station = True
	station_ids = []
	s_id = -1
	for result in cursor:
		if result[1] == station_addr:
			add_station = False
			s_id = result[0]
		station_ids.append(result[0])
	
	if add_station == True:
		new_id = max(station_ids) + 1
		cmd = 'INSERT INTO station(station_id, address) VALUES (:s_id, :s_addr)';
		s_id = new_id
		g.conn.execute(text(cmd), s_id=new_id, s_addr=station_addr)

	cursor = g.conn.execute("SELECT * FROM locates")
	add_locates = True
	for result in cursor:
		if result[0] == session.get('location_id', None):
			add_locates = False
	print("line 365 s_id is", s_id)
	if add_locates == True:
		cmd = 'INSERT INTO locates(location_id, station_id) VALUES (:l_id, :s_id)'
		g.conn.execute(text(cmd), l_id=session.get('location_id', None), s_id=s_id)

	# TODO: check duplicate?
	cmd = 'INSERT INTO consists(route_id, station_id) VALUES (:route_id, :station_id)'
	g.conn.execute(text(cmd), route_id=route_id, station_id=s_id)

	# TODO: check duplicate?
	cmd = 'INSERT INTO train(train_id) VALUES (:train_id)'
	g.conn.execute(text(cmd), train_id=train_id)

	user_name = session.get('user_name')
	session['closest_station'] = station_addr
	context = dict(data = [session.get('location_addr'), session.get('location_type'), session.get('business_hour'), station_addr])
	return render_template("input_summary.html", **context)

@app.route('/logout', methods=["POST"])	
def logout():
	session.pop('user_name', None)
	session.pop('user_id', None)
	session.pop('location_id', None)
	session.pop('business_hour', None)
	session.pop('location_type', None)
	session.pop('location_addr', None)
	session.pop('closest_station', None)
	return render_template("index.html")

		
	

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
