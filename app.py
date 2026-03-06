from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


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
    app.run(debug=True)