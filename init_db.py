import sqlite3

def init_db():
    conn = sqlite3.connect("keeper.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("It worked! Database initialized. Congrats!")

if __name__ == "__main__":
    init_db()

