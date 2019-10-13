from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
app.secret_key="itsasecrettoeverybody"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)


@app.route("/")
def login_or_reg():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    is_valid = True
    if not request.form["fname"].isalpha() or not len(request.form["fname"]) >=2:
        is_valid = False
        flash("First name can only contain letters and must be at least 2 characters long")
    if not request.form['lname'].isalpha() or not len(request.form['lname']) >= 2:
        is_valid = False
        flash("Last name can only contain letters and must be at least 2 characters long")
    if not EMAIL_REGEX.match(request.form["email"]):
        is_valid = False
        flash("Invalid Email Address")
    if len(request.form["password"]) < 8:
        is_valid = False
        flash("Password must be at least 8 characters long")
    if request.form["password"] != request.form["confirmpass"]:
        is_valid = False
        flash("Passwords do not match")
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        mysql = connectToMySQL("thoughts_db")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(password)s, NOW(), NOW())"
        data = {
            "fname": request.form["fname"],
            "lname": request.form["lname"],
            "email": request.form["email"],
            "password": pw_hash
        }
        user_id = mysql.query_db(query, data)
        session["user_id"] = user_id
        print(user_id)
        return redirect("/thoughts")

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    mysql = connectToMySQL("thoughts_db")
    query = "SELECT * FROM users WHERE users.email = %(email)s"
    data = {
        "email": request.form["email"]
    }
    user = mysql.query_db(query, data)
    if user:
        hashed_pw = user[0]["password"]
        if bcrypt.check_password_hash(hashed_pw, request.form['pass']):
            session["user_id"] = user[0]["user_id"]
            return redirect("/thoughts")
        else:
            flash("Invalid Password")
            return redirect("/")
    else:
        flash("Email not in Database")
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/thoughts")
def user_landing():
    if "user_id" not in session:
        return redirect("/")
    mysql = connectToMySQL("thoughts_db")
    query = "SELECT * FROM users WHERE users.user_id = %(id)s"
    data = {'id': session['user_id']}
    user = mysql.query_db(query, data)

    mysql = connectToMySQL("thoughts_db")
    query = "SELECT thoughts.thought_id, thoughts.author, thoughts.content, thoughts.created_at, users.first_name, COUNT(user_likes.thought_like) as like_count FROM thoughts JOIN users ON thoughts.author = users.user_id  LEFT JOIN user_likes on thoughts.thought_id = thought_like GROUP BY thought_id ORDER BY like_count desc"
    thoughts_data = mysql.query_db(query)

    mysql = connectToMySQL("thoughts_db")
    query = "SELECT thought_like, COUNT(thought_like) as like_count FROM user_likes GROUP BY thought_like"
    like_count = mysql.query_db(query)

    return render_template("user_landing.html", user_data = user[0], thoughts_data=thoughts_data, like_count = like_count)

@app.route("/create_thought", methods=["POST"])
def create_thought():
    if "user_id" not in session:
        return redirect("/")
    is_valid = True
    if len(request.form["thought_content"]) < 6:
        is_valid = False
        flash("Thoughts must be longer than 5 characters.", "false")
    if is_valid:
        mysql = connectToMySQL("thoughts_db")
        query = "INSERT INTO thoughts (content, author, created_at, updated_at) VALUES (%(content)s, %(author)s, NOW(), NOW())"
        data = {
            "content": request.form["thought_content"],
            "author": session["user_id"]
        }
        mysql.query_db(query, data)
        flash("Thought added!", "true")
    return redirect("/thoughts")

@app.route("/delete_thought/<thought_id>")
def delete_thought(thought_id):
    if "user_id" not in session:
        return redirect("/")
    mysql = connectToMySQL("thoughts_db")
    query = "DELETE FROM thoughts WHERE author = %(user_id)s and thought_id = %(thought_id)s"
    data = {
        "user_id": session["user_id"],
        "thought_id": thought_id
    }
    mysql.query_db(query, data)
    return redirect("/thoughts")

@app.route("/<thought_id>")
def thought_details(thought_id):
    if "user_id" not in session:
        return redirect("/")
    mysql = connectToMySQL("thoughts_db")
    query = "SELECT thoughts.author, thoughts.thought_id, thoughts.content, users.first_name FROM thoughts JOIN users ON thoughts.author = users.user_id WHERE thoughts.thought_id = %(thought_id)s"
    data = {"thought_id": thought_id}
    thought_data = mysql.query_db(query,data)

    mysql = connectToMySQL("thoughts_db")
    query = "SELECT thought_like from user_likes WHERE user_like= %(user_id)s"
    data = {"user_id": session["user_id"]}
    liked_thoughts = [thought["thought_like"] for thought in mysql.query_db(query, data)]

    mysql = connectToMySQL("thoughts_db")
    query = "SELECT users.user_id, users.first_name, users.last_name FROM user_likes JOIN users ON user_likes.user_like = users.user_id WHERE thought_like = %(thought_id)s"
    data = {
        "thought_id": thought_id
    }
    users_liked = mysql.query_db(query,data)

    return render_template("thought_details.html", thought = thought_data[0], liked_thoughts = liked_thoughts, users_liked = users_liked)

@app.route("/like/<thought_id>")
def like_thought(thought_id):
    if "user_id" not in session:
        return redirect("/")

    mysql = connectToMySQL("thoughts_db")
    query = "INSERT INTO user_likes (user_like, thought_like) VALUES (%(user_id)s, %(thought_id)s)"
    data = {
        "user_id": session["user_id"],
        "thought_id": thought_id
    }
    mysql.query_db(query, data)
    # return redirect(f"/{thought_id}")
    return redirect("/{}".format(thought_id))

@app.route("/unlike/<thought_id>")
def unlike_thought(thought_id):
    if "user_id" not in session:
        return redirect("/")

    mysql = connectToMySQL("thoughts_db")
    query = "DELETE FROM user_likes WHERE user_like = %(user_id)s and thought_like = %(thought_id)s"
    data = {
        "user_id": session["user_id"],
        "thought_id": thought_id
    }
    mysql.query_db(query, data)
    # return redirect(f"/{thought_id}")
    return redirect("/{}".format(thought_id))
if __name__ == "__main__":
    app.run(debug=True)
