from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import urllib.request as req

app = Flask(__name__)

app.secret_key = 'your secret key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sumanth@6302'
app.config['MYSQL_DB'] = 'geeklogin'

mysql = MySQL(app)

# API key and URLs for movie data
api_key = "be818da11c73be0dcfaf55ed686daa7d"
base_urls = [
    {"url": f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}", "category": "popular"},
    {"url": f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}", "category": "top_rated"},
    {"url": f"https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}", "category": "upcoming"}
]

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        movie_data = []
        for url in base_urls:
            conn = req.urlopen(url["url"])
            response_data = conn.read()
            json_data = json.loads(response_data)
            for movie in json_data["results"]:
                movie["category"] = url["category"]
            movie_data.extend(json_data["results"])
        return render_template("indexs.html", data=movie_data)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0')
