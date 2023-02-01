import os
#import mysql.connector
import sqlite3
import hashlib
from sqlite3 import Error
from flask import Flask, flash, request, redirect, url_for, render_template, abort, session
from werkzeug.utils import secure_filename
from datetime import datetime

SESSION_TYPE = 'memcache'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.heif', '.gif']
app.secret_key = 'BAD_SECRET_KEY'

#dataBase = mysql.connector.connect(
#    host ="hostname",
#    user="username",
#    passwd="password",
#    database="database name"
#)

#cursorObject = dataBase.cursor()

#dataBase.close()

connection = sqlite3.connect("/FileUploadSite/db/Data.db")
cursor = connection.cursor()

create_table_logins = """
CREATE TABLE IF NOT EXISTS logins (
username VARCHAR(5),
password VARCHAR(32)
);"""

cursor.execute(create_table_logins)
connection.commit()
connection.close()

@app.errorhandler(413)
def pagenotfound(e):
    return render_template(
        "index.html",
        MessageUploadTooBig = 'File is too big. Max Size is 5mb.'
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' in session:
        file = request.files['file']
        original_filename = file.filename
        print(original_filename)
        filename = secure_filename(file.filename)
        print(filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template(
                "index.html",
                MessageUploadNotOK = 'Wrong File Extension. Only JPG, JPEG, PNG, HEIF and GIF allowed.'
            )
        save_filename = '/Saved_Data/%s'%datetime.now().strftime('%Y-%d-%m--%H-%M-%S') + file_ext
        print(save_filename)
        file.save(save_filename)
        return render_template(
            "index.html",
            MessageUploadOk = 'File uploaded successfully'
        )

@app.route('/login', methods=['POST'])
def login_form():
    try:
        username = request.form['uname']
        print(username)
        str2hash = request.form['psw']
        password = hashlib.md5(str2hash.encode())
        str2hash = "None"
        connection = sqlite3.connect("/FileUploadSite/db/Data.db")
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM logins WHERE username = '%s'" % username)
        passwordhashsql = cursor.fetchall()
        connection.close()
        passwordhash = passwordhashsql[0][0]
        #dataBase = mysql.connector.connect(
        #    host ="localhost",
        #    user="root",
        #    passwd="mysqldev",
        #    database="login"
        #)
        #cursorObject = dataBase.cursor()
        #query = "SELECT password FROM logins WHERE username = '%s'" % username
        #cursorObject.execute(query)
        #passwordhashsql = cursorObject.fetchall()
        #print(passwordhashsql)
        #passwordhash = passwordhashsql[0][0]
        #print(passwordhash)
        #print(password.hexdigest())
        if password.hexdigest() == passwordhash:
            session['username'] = username
            return redirect ('/main')
        else:
            return render_template(
                "login.html",
                MessageLoginNotOK = 'Error: Wrong Username or Password'
            )
    except:
        return render_template(
            "login.html",
            MessageLoginNotOK = 'Error: Wrong Username or Password'
        )
    

@app.route("/main")
def hello_there(name = None):
    if 'username' in session:
        return render_template(
            "index.html"
        )

@app.route("/")
def login(name = None):
    return render_template(
        "login.html"
    )

if __name__ == '__main__':
    app.run(debug=True)