from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

import json, pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime

from helpers import *

app = Flask(__name__)
app.config.from_object("config")

mongo = pymongo.MongoClient(app.config["MONGO_CONNECTION_URI"], maxPoolSize=50, connect=False)
db = pymongo.database.Database(mongo, app.config["MONGO_DATABASE"])


@app.route("/", methods=['GET', 'POST'])
def index():
	
	username = None
	role = None

	if 'sort-option' in request.form: 
		sort = request.form['sort-option']
	else:
		sort = 'date-dec'

	col = pymongo.collection.Collection(db, 'photos')
	col_results = json.loads(dumps(col.find({'approved':True})))
	sorted_col_results = col_results

	if sort == 'likes-dec':
		sorted_col_results = sorted(col_results, key = lambda i: len(i['likes']), reverse=True )
	elif sort == 'likes-cre':
		sorted_col_results = sorted(col_results, key = lambda i: len(i['likes']))
	elif sort == 'date-dec':
		sorted_col_results = sorted(col_results, key = lambda i: (i['date_added']['$date']), reverse=True ) 
	elif sort ==  'date-cre':
		sorted_col_results = sorted(col_results, key = lambda i: (i['date_added']['$date']) ) 

	if 'username' in session:
		username = session['username']
	
	if 'role' in session:
		role = session['role']
			
		
	return render_template("index.html", username=username, role=role, photos=sorted_col_results)

@app.route("/like", methods=['POST'])
def like():

	if 'username' not in session:
		return redirect(url_for('index'))

	col = pymongo.collection.Collection(db, 'photos')
	col_results = json.loads(dumps(col.find({'_id':ObjectId(request.form['id'])})))

	if request.form['like'] == 'like':
		col_results[0]['likes'].append(session['username'])		
	elif request.form['like'] == 'dislike':
		col_results[0]['likes'].remove(session['username'])
	col.update_one({'_id':ObjectId(request.form['id'])}, {'$set': {'likes':col_results[0]['likes']}})	

	return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error_msg = None
	if 'username' in session:
		return redirect(url_for('index'))
	else:
		if request.method == 'POST':
			col = pymongo.collection.Collection(db, 'users')
			col_results = json.loads(dumps(col.find({"name":request.form['username']})))
			
			if col_results and col_results[0]['password'] == request.form['password']:

				session['username'] = request.form['username']
				session['role'] = col_results[0]['role']

				return redirect(url_for('index'))
			else:
				error_msg = "User or password incorrect!"
		return render_template("login.html", error_msg=error_msg, username=None, role=None)    

@app.route('/logout')
def logout():
    # remove the username and role from the session if it's there
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))


# for testing
@app.route("/db")
def database(): 
	col = pymongo.collection.Collection(db, 'users')
	col_results = json.loads(dumps(col.find()))
	print(col_results)

	return str(col_results)


@app.route("/submit_photo", methods=['GET','POST'])
def submit_photo():

	if 'username' in session:	
		if request.method == 'POST':
			if "user_file" not in request.files:
				return render_template("submit_photo.html", username=session['username'], msg ="No user_file key in request.files" )

			file = request.files["user_file"]
			print(file)
			if file.filename == "":
				return render_template("submit_photo.html", username=session['username'], msg="Please select a file")			

			if file and allowed_file(file.filename):
				file.filename = secure_filename(file.filename)
				output   	  = upload_file_to_s3(file, app.config["S3_BUCKET"])

				col = pymongo.collection.Collection(db, 'photos')

				photo = { "url": output, "approved": False , "likes": [], "date_added":datetime.utcnow()}
				x = col.insert_one(photo)
				
				return render_template("submit_photo.html", username=session['username'], msg="Photo uploaded. waiting for approval...")
			
		return render_template("submit_photo.html" , username=session['username'], role=session['role'], msg=None)
	else:
		return redirect(url_for('index'))

# for testing
@app.route("/disapprove", methods=['GET','POST']) 
def disapprove(): 
	col = pymongo.collection.Collection(db, 'photos')
	col.update_many({}, {'$set': {'approved':False}})
	return redirect(url_for('index'))


@app.route("/approve", methods=['GET','POST'])
def approve():

	if request.method == 'POST':
		col = pymongo.collection.Collection(db, 'photos')
		col.update_one({'_id':ObjectId(request.form['id'])}, {'$set': {'approved':True}})

	if 'username' in session and 'role' in session and session['role']=='wed':
		col = pymongo.collection.Collection(db, 'photos')
		col_results = json.loads(dumps(col.find({'approved':False})))
	
		return render_template("approve.html" , username=session['username'], role=session['role'], msg=None, photos=col_results)

	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(port="8989")