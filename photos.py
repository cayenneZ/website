from flask import render_template, redirect, url_for, request, g, session
from app import webapp

import mysql.connector
import tempfile
import os

from wand.image import Image

from app.config import db_config


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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

@webapp.route('/',methods=['GET'])
@webapp.route('/album',methods=['GET'])
#Return html with thumbnails of all photos for the current user
def thumbnails():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    cnx = get_db()

    cursor = cnx.cursor()

    query = "SELECT p.id, t.filename " \
            "FROM photo p, transformation t " \
            "WHERE p.id = t.photo_id AND " \
            "      t.type_id = 2 AND " \
            "      p.user_id = %s "

    try:
        cursor.execute(query, (session['user_id'],))
    except Exception as e:
        return e.msg

    return render_template("photos/album.html",cursor=cursor)

@webapp.route('/photo/<int:photo_id>',methods=['GET'])
#Return html with alls the versions of a given photo
def details(photo_id):
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    try:
        cnx = get_db()
        cursor = cnx.cursor()

        # create a new tuple for the photo and store the
        query = "SELECT t.filename " \
                "FROM transformation t, photo p " \
                "WHERE t.photo_id = p.id AND " \
                "      p.id = %s AND " \
                "      p.user_id = %s AND " \
                "      t.type_id <> 2"
        cursor.execute(query,(photo_id,session['user_id']))

    except Exception as e:
            return e.msg

    return render_template("photos/details.html",cursor=cursor)




@webapp.route('/upload_form',methods=['GET'])
#Returns an html form for uploading a new photo
def upload_form():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    e = None

    if 'error' in session:
        e = session['error']
        session.pop('error')


    return render_template("photos/upload_form.html", error=e)

#Helper function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@webapp.route('/upload_save',methods=['POST'])
#Handles photo upload and the creation of a thumbnail and three transformations
def upload_save():
    if 'authenticated' not in session:
        return redirect(url_for('upload_form'))

    # check if the post request has the file part
    if 'uploadedfile' not in request.files:
        session['error'] = "Missing uploaded file"
        return redirect(url_for('upload_form'))

    new_file = request.files['uploadedfile']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        session['error'] = 'Missing file name'
        return redirect(url_for('upload_form'))

    if allowed_file(new_file.filename) == False:
        session['error'] = 'File type not supported'
        return redirect(url_for('upload_form'))


    fname = os.path.join('app/static/user_images', new_file.filename)

    new_file.save(fname)

    try:
        cnx = get_db()
        cursor = cnx.cursor()

        # create a new tuple for the photo and store the
        query = "INSERT INTO photo (user_id) VALUES (%s)"
        cursor.execute(query,(session['user_id'],))

        # get id of newly created tuple
        query = "SELECT LAST_INSERT_ID()"
        cursor.execute(query)

        row = cursor.fetchone()

        photo_id = row[0]

        # store the path to the original image
        query = "INSERT INTO transformation (filename,type_id,photo_id) VALUES (%s,%s,%s)"

        cursor.execute(query, (fname[4:],1,photo_id))

        # create thumbnail
        img = Image(filename=fname)
        i = img.clone()
        i.resize(50, 60)
        fname_thumbnail = os.path.join('app/static/user_images', 'thumbnail_' + new_file.filename)
        i.save(filename=fname_thumbnail)

        # store path to thumbnail
        query = "INSERT INTO transformation (filename,type_id,photo_id) VALUES (%s,%s,%s)"
        cursor.execute(query, (fname_thumbnail[4:], 2, photo_id))

        create_and_store_transformation(img, cursor, 3, new_file.filename, photo_id)

        create_and_store_transformation(img, cursor, 4, new_file.filename, photo_id)

        create_and_store_transformation(img, cursor, 5, new_file.filename, photo_id)



        cursor.close()

        cnx.commit()

    except Exception as e:
        cnx.rollback()

    return redirect(url_for('thumbnails'))


@webapp.route('/test/FileUpload',methods=['POST'])
#Entry point for automatic testing
def test_upload():
    cnx = get_db()

    cursor = cnx.cursor()

    query = "SELECT * FROM user WHERE username = %s"

    cursor.execute(query, (request.form['userID'],))

    row = cursor.fetchone()

    if row != None:
        session['authenticated'] = True
        session['username'] = request.form['userID']
        session['user_id'] = row[0]
        upload_save()
        return "OK"

    return "Error"

def create_and_store_transformation(img, cursor, trans_id, filename, photo_id):
    # create transformation
    i = img.clone()
    i.rotate(90*trans_id)
    fname_transformation = os.path.join('app/static/user_images', 'transformation_' + str(trans_id) + "_" + filename)
    i.save(filename=fname_transformation)

    # store path to thumbnail
    query = "INSERT INTO transformation (filename,type_id,photo_id) VALUES (%s,%s,%s)"
    cursor.execute(query, (fname_transformation[4:], trans_id, photo_id))
    return


