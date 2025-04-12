from flask import Flask, render_template, request
import joblib
import pandas as pd
from datetime import datetime
import requests
import os

app = Flask(__name__)

# Load the trained model
model = joblib.load("models/xgb_model.joblib")

# TomTom API key
TOMTOM_API_KEY = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

def get_coordinates_from_location(location_name):
    url = f"https://api.tomtom.com/search/2/geocode/{location_name}.json?key={TOMTOM_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data["results"]:
        position = data["results"][0]["position"]
        return position["lat"], position["lon"]
    else:
        return None, None

def get_day_hour_from_input(time_str):
    try:
        dt = datetime.strptime(time_str, "%H:%M")
        return datetime.today().weekday(), dt.hour
    except ValueError:
        return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        home = request.form["home"]
        office = request.form["office"]
        time_input = request.form["time"]

        # Get lat/lon
        home_lat, home_lon = get_coordinates_from_location(home)
        office_lat, office_lon = get_coordinates_from_location(office)

        if None in [home_lat, home_lon, office_lat, office_lon]:
            return render_template("index.html", error="Invalid home or office location entered.")

        # Get time features
        day_of_week, hour_of_day = get_day_hour_from_input(time_input)
        if day_of_week is None:
            return render_template("index.html", error="Invalid time format. Please use HH:MM.")

        # Predict
        input_df = pd.DataFrame([{
            "start_lat": home_lat,
            "start_lng": home_lon,
            "end_lat": office_lat,
            "end_lng": office_lon,
            "day_of_week": day_of_week,
            "hour_of_day": hour_of_day
        }])

        predicted_duration = model.predict(input_df)[0]
        predicted_duration = round(predicted_duration, 2)

        return render_template("index.html", prediction=predicted_duration)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
