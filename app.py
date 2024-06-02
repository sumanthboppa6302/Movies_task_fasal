from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re
import json
import urllib.request as req

app = Flask(__name__)

app.secret_key = 'your secret key'

# MySQL configurations
db_config = {
    'host': 'SumanthBoppa03.mysql.pythonanywhere-services.com',
    'user': 'SumanthBoppa03',
    'password': 'Sumanth@123',
    'database': 'SumanthBoppa03$Movies'
}

# API key and URLs for movie data
api_key = "be818da11c73be0dcfaf55ed686daa7d"
base_urls = [
    {"url": f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}", "category": "popular"},
    {"url": f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}", "category": "top_rated"},
    {"url": f"https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}", "category": "upcoming"}
]

def check_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        conn.close()
        return True
    except mysql.connector.Error as e:
        return False

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if check_db_connection():
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
            account = cursor.fetchone()
            conn.close()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username / password!'
        else:
            msg = 'Failed to connect to the database.'
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
        if check_db_connection():
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
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
                conn.commit()
                msg = 'You have successfully registered!'
                conn.close()
        else:
            msg = 'Failed to connect to the database.'
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
    app.run(debug=True, host='0.0.0.0')
