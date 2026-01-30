from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "miniflix_secret"

UPLOAD_FOLDER = "static/videos"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_db():
    return sqlite3.connect("database.db")

# ---------- DATABASE ----------
def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        video TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        user_id INTEGER,
        movie_id INTEGER
    )
    """)

    db.commit()
    db.close()

# ---------- USER AUTH ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()

        if user:
            session["user"] = user[0]
            return redirect("/home")

    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO users VALUES (NULL,?,?)",
                    (request.form["username"], request.form["password"]))
        db.commit()
        return redirect("/")
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- HOME ----------
@app.route("/home")
def home():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM movies")
    movies = cur.fetchall()
    return render_template("home.html", movies=movies)

# ---------- MOVIE ----------
@app.route("/movie/<int:id>")
def movie(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM movies WHERE id=?", (id,))
    movie = cur.fetchone()
    return render_template("movie.html", movie=movie)

# ---------- WATCHLIST ----------
@app.route("/add_watchlist/<int:id>")
def add_watchlist(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO watchlist VALUES (?,?)", (session["user"], id))
    db.commit()
    return redirect("/watchlist")

@app.route("/watchlist")
def watchlist():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT movies.* FROM movies
    JOIN watchlist ON movies.id = watchlist.movie_id
    WHERE watchlist.user_id=?
    """,(session["user"],))
    movies = cur.fetchall()
    return render_template("watchlist.html", movies=movies)

# ================= ADMIN =================

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == ADMIN_USERNAME and
            request.form["password"] == ADMIN_PASSWORD):
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM movies")
    movies = cur.fetchall()
    return render_template("admin_dashboard.html", movies=movies)

@app.route("/admin/add_movie", methods=["POST"])
def admin_add_movie():
    if "admin" not in session:
        return redirect("/admin")

    title = request.form["title"]
    description = request.form["description"]
    video = request.files["video"]

    if video:
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
        video.save(video_path)

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO movies VALUES (NULL,?,?,?)",
                    (title, description, video.filename))
        db.commit()

    return redirect("/admin/dashboard")

@app.route("/admin/delete/<int:id>")
def admin_delete(id):
    if "admin" not in session:
        return redirect("/admin")

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM movies WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/dashboard")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

# ---------- RUN ----------
if __name__ == "__main__":
    os.makedirs("static/videos", exist_ok=True)
    init_db()
    app.run(debug=True)
