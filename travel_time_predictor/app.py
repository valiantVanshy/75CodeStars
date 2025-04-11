from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)
TOMTOM_API_KEY = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
        source_lat = request.form["source_lat"]
        source_lon = request.form["source_lon"]
        dest_lat = request.form["dest_lat"]
        dest_lon = request.form["dest_lon"]

        url = (
            f"https://api.tomtom.com/routing/1/calculateRoute/"
            f"{source_lat},{source_lon}:{dest_lat},{dest_lon}/json"
            f"?key={TOMTOM_API_KEY}&traffic=true"
        )

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("routes"):
                eta_seconds = data["routes"][0]["summary"]["travelTimeInSeconds"]
                eta_minutes = round(eta_seconds / 60, 2)
                prediction = f"{eta_minutes} minutes"
            else:
                prediction = "No route found!"
        else:
            prediction = "Error fetching route from TomTom."

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
