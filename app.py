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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        name TEXT,
        team TEXT,
        role TEXT,
        matches INTEGER,
        runs INTEGER,
        wickets INTEGER,
        base_price INTEGER,
        current_bid INTEGER
    )
    """)

    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()[0]

    if count == 0:

        cur.execute("""
        INSERT INTO players
        (name,team,role,matches,runs,wickets,base_price,current_bid)
        VALUES

        ('Virat Kohli','RCB','Batsman',237,7263,4,20000000,20000000),
        ('Rohit Sharma','MI','Batsman',243,6211,15,20000000,20000000),
        ('MS Dhoni','CSK','WK-Batsman',250,5082,0,20000000,20000000),
        ('Jasprit Bumrah','MI','Bowler',133,69,165,20000000,20000000),
        ('Hardik Pandya','GT','All-Rounder',123,2309,53,15000000,15000000),
        ('KL Rahul','LSG','WK-Batsman',118,4163,0,17000000,17000000),
        ('Shubman Gill','GT','Batsman',91,2790,0,18000000,18000000),
        ('Ravindra Jadeja','CSK','All-Rounder',226,2692,152,16000000,16000000),
        ('Andre Russell','KKR','All-Rounder',112,2262,96,15000000,15000000),
        ('David Warner','DC','Batsman',176,6397,0,18000000,18000000)

        """)
        conn.commit()

    cur.close()
    conn.close()

init_db()

@app.route("/")
def index():

    team = request.args.get("team")
    role = request.args.get("role")

    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM players WHERE 1=1"
    params = []

    if team:
        query += " AND team=%s"
        params.append(team)

    if role:
        query += " AND role=%s"
        params.append(role)

    cur.execute(query, params)
    players = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", players=players)


@app.route("/player/<int:player_id>")
def player_stats(player_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players WHERE id=%s",(player_id,))
    player = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("player.html", player=player)


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
            (bid_amount,player_id)
        )
        conn.commit()

    cur.close()
    conn.close()

    return redirect("/")