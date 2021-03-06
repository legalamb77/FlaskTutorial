#imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash
from datetime import datetime
app=Flask(__name__) #application instance creation!
app.config.from_object(__name__) #loading config from this file (name refers to this file, flaskr.py
f=open('secret.txt','r')
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY=f.read(),
    USERNAME='admin',
    PASSWORD='default'
))
f.close()
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row #treats row in db as a dictionary object
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes database"""
    init_db()
    print("Initialized the database.")

def get_db():
    """
    opens a new database connection if there is not yet one for the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes database again at end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text, time from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db=get_db()
    db.execute('insert into entries (title, text, time) values (?,?,?)',
            [request.form['title'], request.form['text'], datetime.now().strftime("%I:%M %p, %B %d, %Y")])
    db.commit()
    flash('New entry was successfully posted!')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method=='POST':
        if request.form['username'] != app.config['USERNAME']:
            error='invalid username!'
        elif request.form['password'] != app.config['PASSWORD']:
            error='invalid password!'
        else:
            session['logged_in']=True
            flash('You have been logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out')
    return redirect(url_for('show_entries'))
