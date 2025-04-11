from flask import Flask, render_template, request
import pandas as pd
import joblib
import datetime

app = Flask(__name__)

# ✅ Load location data and model
locations_df = pd.read_csv("data/bangalore_locations.csv")  # Columns: name, lat, lon
location_names = sorted(locations_df["name"].unique())
model = joblib.load("models/xgb_model.joblib")

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        source = request.form["source"]
        destination = request.form["destination"]

        if source == destination:
            prediction = "Source and destination are the same. ETA is 0 minutes."
        else:
            # 🔍 Lookup coordinates
            source_row = locations_df[locations_df["name"] == source].iloc[0]
            dest_row = locations_df[locations_df["name"] == destination].iloc[0]

            start_lat = source_row["lat"]
            start_lon = source_row["lon"]
            end_lat = dest_row["lat"]
            end_lon = dest_row["lon"]

            # 🕒 Get time info
            now = datetime.datetime.now()
            day_of_week = now.weekday()
            hour = now.hour

            # 📊 Predict with model
            features = [[start_lat, start_lon, end_lat, end_lon, day_of_week, hour]]
            duration = model.predict(features)[0]
            prediction = f"Estimated Travel Time from {source} to {destination} = {round(duration)} minutes"

    return render_template("index.html", locations=location_names, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
