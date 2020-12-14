#!/usr/bin/python
# -*- coding: utf-8 -*-
#Lang Tuang | 12/12/2020 |Final Project of IS211

#all module
import urllib
import json
import pickle
import time
import re
import sqlite3
import os.path
import urllib.request
from datetime import timedelta
from flask import Flask,abort, render_template, request, redirect, session, url_for, g,flash

#database configuration
DATABASE = 'bookshelf.db'
DEBUG = True
SECRET_KEY = 'happy'
USERNAME = 'admin'
PASSWORD = 'password'

#flask app
app  = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(hours = 1)

#GOOGLEAPI URL
url2api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
#SQL Connection Object
def connect_database():
	return sqlite3.connect(app.config['DATABASE']



#before_request: decorator allows to create a function that will run before each request.
@app.before_request
def before_request():
	g.db = connect_database()

#teardown_request: cleanup operations after requests
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with closing(connect_database()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#addbook
@app.route('/adds', methods =['POST'])
def adds():
	try:
		queryy = ('INSERT INTO bookshelf (ISBN, TITLE, AUTHORS, PAGECOUNT, AVERAGERATING, THUMBNAIL) VALUES (?,?,?,?,?,?)'
		g.db.execute(queryy,
			(request.form['isbn'],
			request.form['title'],
			request.form['authors'],
			request.form['pagecount'],
			request.form['averagerating'],
			request.form['thumbnail']))
		g.db.commit()
		flash("Hey your book is added to the shelf")
		return redirect(url_for('homepage'))

	except():
		flash("Umm...something went wrong. Please try again.")
		return redirect(url_for('homepage'))


#deletebook
@app.route('/deletes', methods = ['GET'])
def deletes():
	id = request.args.get('id')
	queryy = "DELECT FROM bookshelf WHERE ID = ?"
	g.db.execute(queryy,(id))
	g.db.commit()
	flash("Deleted your book from the shelf")
	return redirect(url_for('homepage'))






#Page1: Login Page
@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		session.permanent = True
		if request.form['username'] != 'username':
			error = "You entered wrong username or password."
		elif request.form['password'] != 'password':
			error = "You entered wrong username or password."
		else:
			session['logged_in'] = True
			flash("Thank you for logging in")
			return redirect(url_for('homepage'))
	return render_template('login.html', error = error)

#Page2: Logout Page --redirect to homepage
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash("Sorry to see you leave. See you soon?", "info")
	return redirect(url_for('homepage'))

#page3: Lookup Page -- to check if the book exist in the library
@app.route('/lookup', methods=['POST','GET'])
def lookup():
	isbn = None

	if request.method == 'POST':
		isbn = request.form['ISBN']
		if isbn != "":
			try:
				completeurl = url2api + isbn
				response = urllib.request.urlopen(completeurl)
				data = html.read()
				data = json.loads(data)
				volume = data['items'][0]['volumeInfo']
				title = volume['title']
				authors = volume['authors'][0]
				pagecount = volume['pageCount']
				averagerating = volume['averageRating']
				thumbnail = volume['imgaeLinks']['smallThumbnail']
				return render_template('lookup.html',
										thumbnail=thumbnail,
										title=title,
										authors=authors,
										pagecount=pagecount,
										averagerating=averagerating,
										isbn=isbn)
			except:
				flash("Check the ISBN number and try again")
				return redirect(url_for('lookup'))
		else:
			flash("You should enter ISBN number  now__")
			return redirect(url_for('lookup'))
    elif request.method == 'GET':
        return render_template('lookup.html')

#Page4: Home Page
@app.route('/')
def homepage():
	queryy = "SELECT ID, ISBN, TITLE, AUTHORS, PAGECOUNT, AVERAGERATING, THUMBNAIL FROM bookshelf"
	cur = g.db.execute(queryy)
	books = [dict(id =row[0], 
			isbn = row[1], 
			title= row[2],
			authors = row[3],
			pageCount= row[4],
			averagerating = row[5],
			thumbnail = row[6]) for row in cur.fetchall()]	
	return render_template('index.html')





if __name__ == "__main__":
	app.run(debug= DEBUG)