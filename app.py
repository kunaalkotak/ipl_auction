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

    # DELETE OLD TABLE
    cur.execute("DROP TABLE IF EXISTS players")

    cur.execute("""
    CREATE TABLE players(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT,
        team TEXT,
        base_price INTEGER,
        current_bid INTEGER,
        matches INTEGER,
        runs INTEGER,
        wickets INTEGER
    )
    """)

    cur.execute("""
    INSERT INTO players
    (name,role,team,base_price,current_bid,matches,runs,wickets)

    VALUES

    ('Virat Kohli','Batsman','RCB',20000000,20000000,237,7263,4),
    ('Rohit Sharma','Batsman','MI',20000000,20000000,243,6211,15),
    ('Jasprit Bumrah','Bowler','MI',20000000,20000000,120,56,145),
    ('MS Dhoni','Wicketkeeper','CSK',20000000,20000000,250,5082,0),
    ('Hardik Pandya','All-Rounder','MI',15000000,15000000,123,2309,53),
    ('Ravindra Jadeja','All-Rounder','CSK',15000000,15000000,226,2692,152),
    ('KL Rahul','Batsman','LSG',15000000,15000000,118,4163,0),
    ('Shubman Gill','Batsman','GT',15000000,15000000,91,2790,0),
    ('Andre Russell','All-Rounder','KKR',15000000,15000000,112,2326,96),
    ('Rashid Khan','Bowler','GT',15000000,15000000,109,350,139)
    """)

    conn.commit()

    cur.close()
    conn.close()


init_db()


@app.route("/")
def index():

    role_filter = request.args.get("role")

    conn = get_connection()
    cur = conn.cursor()

    if role_filter:
        cur.execute(
            "SELECT * FROM players WHERE role=%s ORDER BY id",
            (role_filter,)
        )
    else:
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
    app.run(host="0.0.0.0", port=10000)