import os

from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
#@login_required
def index():
    """ Show search box """

    return render_template("layout.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    username = request.form.get("username")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username", 403)

        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        
        if len(userCheck) == 1:
            return ("username already exist", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Ensure confirmation wass submitted 
        elif not request.form.get("confirmation"):
            return ("must confirm password", 403)

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return ("passwords didn't match", 403)
        
        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        
        # Insert register into DB
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                            username=request.form.get("username"), 
                            password=hashedPassword)

        # Redirect user to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")