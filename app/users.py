from flask import render_template, session, request, redirect, url_for, g
from app import webapp

import random

from app.config import db_config

import mysql.connector
import hashlib
import os

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@webapp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@webapp.route('/login', methods=['GET', 'POST'])
def login():
    uname = None
    e = None

    if 'username' in session:
        uname = session['username']

    if 'error' in session:
        e = session['error']
        session.pop('error')


    return render_template("users/login.html", error=e, username=uname)


@webapp.route('/login_submit', methods=['POST'])
def login_submit():
    if 'username' in request.form and 'password' in request.form:
        cnx = get_db()

        cursor = cnx.cursor()

        query = "SELECT * FROM user WHERE username = %s"

        cursor.execute(query, (request.form['username'],))

        row = cursor.fetchone()

        if row != None:
            user_id = row[0]
            username = row[1]
            hash = row[2]
            salt = row[3]

            password = request.form['password']

            salted_password = "{}{}".format(salt, password)
            m = hashlib.md5()
            m.update(salted_password.encode('utf-8'))
            new_hash = m.digest()


            if new_hash == hash:
                session['authenticated'] = True
                session['username'] = request.form['username']
                session['user_id'] = row[0]

                return redirect(url_for('thumbnails'))

    if 'username' in request.form:
        session['username'] = request.form['username']

    session['error'] = "Error! Incorrect username or password!"

    return redirect(url_for('login'))


@webapp.route('/new', methods=['GET', 'POST'])
def new_user():
    uname = None
    e = None

    if 'username' in session:
        uname = session['username']

    if 'error' in session:
        e = session['error']
        session.pop('error')

    return render_template("users/new.html", error=e, username=uname)


@webapp.route('/new_submit', methods=['POST'])
def new_user_submit():
    if 'username' not in request.form or 'password' not in request.form:
        if 'username' in request.form:
            session['username'] = request.form['username']

        session['error'] = "Missing username or password"

        return redirect(url_for('new_user'))

    try:
        cnx = get_db()
        cursor = cnx.cursor()

        query = "INSERT INTO user (username,hash,salt) VALUES (%s,%s,%s)"

        username = request.form['username']
        password = request.form['password']
        salt = str(random.getrandbits(16))
        salted_password = "{}{}".format(salt,password)
        m = hashlib.md5()
        m.update(salted_password.encode('utf-8'))
        hash = m.digest()

        cursor.execute(query,(username, hash, salt))
        cursor.close()

        cnx.commit()
    except Exception as e:
        cnx.rollback()
        session['error'] = str(e)
        return redirect(url_for('new_user'))


    return redirect(url_for('login'))





