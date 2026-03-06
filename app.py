from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            base_price INTEGER NOT NULL,
            current_bid INTEGER NOT NULL
        )
    """)

    # check if table empty
    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("""
            INSERT INTO players (name, base_price, current_bid)
            VALUES
            ('Virat Kohli',20000000,20000000),
            ('Rohit Sharma',20000000,20000000),
            ('Jasprit Bumrah',20000000,20000000),
            ('MS Dhoni',20000000,20000000),
            ('Hardik Pandya',15000000,15000000)
        """)
        conn.commit()

    cur.close()
    conn.close()

@app.route("/")
def index():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players ORDER BY id")
    players = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", players=players)

@app.route("/bid/<int:player_id>", methods=["POST"])
def bid(player_id):

    bid_amount = int(request.form["bid"])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT current_bid FROM players WHERE id=%s",
        (player_id,)
    )

    current_bid = cur.fetchone()[0]

    if bid_amount > current_bid:

        cur.execute(
            "UPDATE players SET current_bid=%s WHERE id=%s",
            (bid_amount, player_id)
        )

        conn.commit()

    cur.close()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)