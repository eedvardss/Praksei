from flask import Flask, render_template, request, redirect, session, jsonify
from apify_client import ApifyClient
import googlemaps
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3
import subprocess



app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///project.db")

client = ApifyClient("apify_api_U87F6gsgqWaWkkC1kV30PZ8l1pEICj3uEocI")
gmaps = googlemaps.Client(key='AIzaSyDmYwKurLlvovZuOfJ6pPLXidmf_yjDZzc')

@app.route('/')
def home():
    return render_template('index.html', page_title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""


    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

        return render_template("main.html")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("Complete all fields!")
        if password != confirmation:
            return apology("Password and confirmation are not the same!")

        if not (
            any(char.isalpha() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in "@$!%*#?&" for char in password)
        ):
            return apology(
                "Passwords must include letters, numbers, and special symbols"
            )

        takenusernames = db.execute("SELECT username FROM users")
        for takenusername in takenusernames:
            if takenusername["username"] == username:
                return apology("Username has been taken!")

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            generate_password_hash(password),
        )

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect('/')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contacts')
@login_required
def contacts():
    return render_template('contacts.html')

@app.route('/homepage')
@login_required
def homepage():
    return render_template('homepage.html')

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

import json

@app.route('/search', methods=['POST'])
def search():
    selected_city = request.form['city']

    run_input = {
        "limit": 150,
        "proxyConfig": {
            "useApifyProxy": True,
            "apifyProxyGroups": []
        },
        "startUrls": [
            {
                "url": f"https://www.ss.lv/en/real-estate/flats/riga/{selected_city}/sell/",
                "method": "POST"
            }
        ]
    }

    run = client.actor("bwrxIkNqoILuzXtiC").call(run_input=run_input)

    dataset_id = run["defaultDatasetId"]
    print("Default Dataset ID:", dataset_id)

    dataset = client.dataset(dataset_id)
    results = list(dataset.iterate_items())

    json_filename = f"dataset_{dataset_id}.json"
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, ensure_ascii=False, indent=2)

    insert_data_into_sqlite(json_filename)

    print(f"Dataset saved to {json_filename}")

    return render_template('main.html', results=results)

def insert_data_into_sqlite(json_filename):
    with open(json_filename, "r") as file:
        json_data = json.load(file)

    conn = sqlite3.connect("project.db")
    cursor = conn.cursor()

    for record in json_data:
        picture_urls = ",".join(record["otherData"]["pictures"]) if "pictures" in record["otherData"] else None

        cursor.execute(
            """
            INSERT INTO real_estate (
                url, title, description, tx_type, price,
                city, neighborhood, street, rooms, flat_floor,
                max_floor, series, building_type, sq_meters, price_per_sq_meter, pictures
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["commonData"]["url"],
                record["commonData"]["title"],
                record["commonData"]["description"],
                record["commonData"]["txType"],
                record["commonData"]["price"],
                record["realEstateData"]["city"],
                record["realEstateData"]["neighborhood"],
                record["realEstateData"]["street"],
                record["realEstateData"]["rooms"],
                record["realEstateData"]["flatFloor"],
                record["realEstateData"]["maxFloor"],
                record["realEstateData"]["series"],
                record["realEstateData"]["buildingType"],
                record["realEstateData"]["sqMeters"],
                record["realEstateData"]["pricePerSqMeter"],
                picture_urls
            )
        )

    conn.commit()
    conn.close()
    subprocess.run(["python", "coordinates.py"])

@app.route('/get_street_locations')
def get_street_locations():
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()


    cursor.execute("SELECT latitude, longitude, description, url, pictures FROM real_estate WHERE latitude IS NOT NULL AND longitude IS NOT NULL")

    locations = cursor.fetchall()

    conn.close()

    locations_with_info = [
        {
            'latitude': row[0],
            'longitude': row[1],
            'description': row[2],
            'url': row[3],
            'pictures': row[4]
        }
        for row in locations
    ]

    return jsonify(locations_with_info)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    connection = sqlite3.connect('project.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM real_estate')

    connection.commit()
    connection.close()

    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
