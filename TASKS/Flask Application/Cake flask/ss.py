import sqlite3

db = sqlite3.connect("database.db")
c = db.cursor()

c.execute("""
UPDATE cakes
SET image = ?
WHERE name = 'Black Forest'
""", (
    "https://images.unsplash.com/photo-1542826438-8b6f3c5caa94?auto=format&fit=crop&w=900&q=80",
))

db.commit()
db.close()

print("Black Forest image fixed ✅")
