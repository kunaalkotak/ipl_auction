from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Home page - show players
@app.route("/")
def index():

    cur = conn.cursor()

    cur.execute("SELECT * FROM players ORDER BY id")

    players = cur.fetchall()

    cur.close()

    return render_template("index.html", players=players)


# Bid route
@app.route("/bid/<int:player_id>", methods=["POST"])
def bid(player_id):

    bid_amount = int(request.form["bid"])

    cur = conn.cursor()

    # Get current bid
    cur.execute(
        "SELECT current_bid FROM players WHERE id=%s",
        (player_id,)
    )

    current_bid = cur.fetchone()[0]

    # Only accept higher bids
    if bid_amount > current_bid:

        cur.execute(
            "UPDATE players SET current_bid=%s WHERE id=%s",
            (bid_amount, player_id)
        )

        conn.commit()

    cur.close()

    return redirect("/")


# Run locally
if __name__ == "__main__":
    app.run(debug=True)