import os

from flask import Flask, session, render_template, url_for, request, redirect, flash
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
database_url = """postgres://uyuytfcwssurku:09d77e0634269dfa5609c6f34051bf637009d0e6ef12b4efa883125ef1601afa@ec2-107-20-155-148.compute-1.amazonaws.com:5432/d3c28q6jpugsl"""
engine = create_engine(os.getenv('database_url'))
db = scoped_session(sessionmaker(bind=engine))

# for password hashing
bcrypt = Bcrypt(app)

loggedin_name = None

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Home', stylefile='homie.css', name=loggedin_name)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        form = request.form
        user_email = form['email']
        user_password = form['password']

        # check user authentication
        user_exist = db.execute('SELECT email FROM users WHERE email=:useremail', {'useremail':user_email}).fetchone()
        if user_exist:
            matching_password = db.execute('SELECT password FROM users WHERE email=:useremail', {'useremail':user_email}).fetchone()
            if bcrypt.check_password_hash(matching_password[0], user_password):
                flash('Logged in successfully.', category='success')
                user_name = db.execute('SELECT name FROM users WHERE email=:useremail', {'useremail':user_email}).fetchone()
                # return render_template('home.html', title='Home', stylefile='homie.css', name=user_name[0])
                global loggedin_name
                loggedin_name=user_name[0]
                print(loggedin_name)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password!', category='danger')
        else:
            flash('Invalid email!', category='danger')

    return render_template('login.html', title='Log in', stylefile='logine.css')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        form = request.form
        user_name = form['name']
        user_email = form['email']
        user_password = form['password']
        user_confirmpassword = form['confirmPassword']
        hashed_password = bcrypt.generate_password_hash(user_password).decode('utf-8')

        # check if email already exists
        found_email = db.execute('SELECT * FROM users WHERE email = :useremail', {'useremail':user_email}).fetchone()
        if found_email:
            flash('Email already exists!', category="danger")
            return render_template('signup.html', title='Sign up', stylefile='signupee.css')
        elif user_confirmpassword != user_password:
            flash('Passwords don\'t match', category="danger")
            return render_template('signup.html', title='Sign up', stylefile='signupee.css')
        else:
            # add user data to database
            db.execute('INSERT INTO users (name, email, password) VALUES (:username, :useremail, :userpassword)', {'username':user_name, 'useremail':user_email, 'userpassword':hashed_password})
            db.commit()
            flash('Account created successfully.', category='success')
            return redirect(url_for('login'))
    else:
        return render_template('signup.html', title='Sign up', stylefile='signupee.css')

@app.route('/logout')
def logout():
    global loggedin_name
    loggedin_name=None
    return redirect(url_for('home'))
