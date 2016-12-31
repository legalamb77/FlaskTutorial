#imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash
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
