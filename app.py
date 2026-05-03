import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session, flash, url_for
import config, db, items, users, secrets

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=items)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []

    return render_template("find_item.html", query=query, results=results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    attributes = items.get_attributes(item_id)
    comments = items.get_comments(item_id)
    return render_template("show_item.html", item=item, attributes=attributes, comments=comments)

@app.route("/new_item")
def new_item():
    require_login()
    attributes = items.get_all_attributes()
    return render_template("new_item.html", attributes=attributes)

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()
    
    title = request.form.get("title", "").strip()
    movie = request.form.get("movie", "").strip()
    review = request.form.get("review", "").strip()
    score_raw = request.form.get("score", "").strip()

    if not title or not movie or len(title) > 50 or len(movie) > 100:
        abort(400)
    if not review or len(review) > 1000:
        abort(400)
    if not (score_raw.isdigit() and 1 <= int(score_raw) <= 100):
        abort(400)

    score = int(score_raw)
    user_id = session["user_id"]

    all_attributes = items.get_all_attributes()

    attributes = []
    for entry in request.form.getlist("attributes[]"):
        if entry:
            attr_title, attr_value = entry.split(":",1)
            if attr_title not in all_attributes:
                abort(400)
            if attr_value not in all_attributes[attr_title]:
                abort(400)
            attributes.append((attr_title, attr_value))

    items.add_item(title, movie, review, score, user_id, attributes)

    return redirect("/")

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form.get("comment", "").strip()
    if not comment or len(comment) > 1000:
        abort(400)
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(400)

    user_id = session["user_id"]

    items.add_comment(item_id, user_id, comment)

    return redirect("/item/" + str(item_id))

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    
    all_attributes = items.get_all_attributes()
    attributes = {}
    for attribute in all_attributes:
        attributes[attribute] = ""
    for entry in items.get_attributes(item_id):
        attributes[entry["title"]] = entry["value"]
    items.get_attributes(item_id)

    return render_template("edit_item.html", item=item, attributes=attributes, all_attributes=all_attributes)

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    title = request.form["title"]    
    movie = request.form["movie"]
    if not title or not movie or len(title) > 50 or len(movie) > 100:
        abort(400)
    review = request.form["review"]
    if not review or len(review) > 1000:
        abort(400)
    score = request.form["score"]
    score_raw = request.form.get("score", "").strip()
    if not (score_raw.isdigit() and 1 <= int(score_raw) <= 100):
        abort(400)
    score = int(score_raw)
    if not score:
        abort(400)
    
    all_attributes = items.get_all_attributes()
    attributes = {}
    for attribute in all_attributes:
        attributes[attribute] = ""
    for entry in items.get_attributes(item_id):
        attributes[entry["title"]] = entry["value"]

    attributes = []
    for entry in request.form.getlist("attributes[]"):
        if entry:
            attr_title, attr_value = entry.split(":",1)
            if attr_title not in all_attributes:
                abort(400)
            if attr_value not in all_attributes[attr_title]:
                abort(400)
            attributes.append((attr_title, attr_value))

    items.update_item(item_id, title, movie, review, score, attributes)

    return redirect("/item/" +str(item_id))

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()
    check_csrf()

    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item=item)

    if request.method == "POST":
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

@app.route("/register")
def register():
    session["csrf_token"] = secrets.token_hex(16)
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    check_csrf()
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "ERROR: passwords do not match"
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "ERROR: username already taken"
    
    flash('Account created successfully')
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
         return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            return "ERROR: wrong username or password"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        del session["csrf_token"]
    return redirect("/")