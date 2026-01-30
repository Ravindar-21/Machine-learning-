from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return sqlite3.connect("database.db")

# ---------------- DATABASE SETUP ----------------
def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        description TEXT,
        image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        cake_id INTEGER
    )
    """)

    # Insert cakes only if empty
    cursor.execute("SELECT COUNT(*) FROM cakes")
    if cursor.fetchone()[0] == 0:
        cakes = [
            ("Chocolate Cake", 500, "Rich chocolate cake",
             "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=80"),

            ("Red Velvet", 700, "Soft red velvet cake",
             "https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?auto=format&fit=crop&w=900&q=80"),

            ("Black Forest", 650, "Chocolate cherry delight",
             "https://images.unsplash.com/photo-1542826438-8b6f3c5caa94?auto=format&fit=crop&w=900&q=80"),

            ("Strawberry Cake", 550, "Fresh strawberry cake",
             "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&w=900&q=80"),

            ("Butterscotch Cake", 600, "Crunchy butterscotch cake",
             "https://images.unsplash.com/photo-1622621746668-59fb299bc4d7?auto=format&fit=crop&w=900&q=80")
        ]

        cursor.executemany(
            "INSERT INTO cakes (name,price,description,image) VALUES (?,?,?,?)",
            cakes
        )
        cursor.execute("""
        UPDATE cakes
        SET image = ?
        WHERE name = 'Black Forest'
        """, (
            "https://images.unsplash.com/photo-1542826438-8b6f3c5caa94?auto=format&fit=crop&w=900&q=80",
        ))
    db.commit()
    db.close()

# ✅ ALWAYS call this BEFORE routes
init_db()

# ---------------- AUTH ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/home")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                (request.form["name"], request.form["email"], request.form["password"])
            )
            db.commit()
            return redirect("/")
        except sqlite3.IntegrityError:
            error = "Email already registered. Please login."

    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- PAGES ----------------
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/cakes")
def cakes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cakes")
    cakes = cursor.fetchall()
    return render_template("cakes.html", cakes=cakes)


@app.route("/order/<int:cake_id>")
def order(cake_id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO orders (user_id,cake_id) VALUES (?,?)",
        (session["user_id"], cake_id)
    )
    db.commit()

    return redirect("/orders")


@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT cakes.name, cakes.price
        FROM orders
        JOIN cakes ON orders.cake_id = cakes.id
        WHERE orders.user_id=?
    """, (session["user_id"],))
    orders = cursor.fetchall()

    return render_template("orders.html", orders=orders)


if __name__ == "__main__":
    app.run(debug=True)
