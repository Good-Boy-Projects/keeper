import sqlite3

def init_db():
    conn = sqlite3.connect("/app/data/keeper.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("It worked !Database initialized. Congrats and welcome!")

if __name__ == "__main__":
    init_db()

