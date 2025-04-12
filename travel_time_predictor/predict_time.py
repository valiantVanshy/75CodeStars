import pandas as pd
import numpy as np
from joblib import load
from sklearn.preprocessing import StandardScaler
import datetime

# === Load model ===
model = load("model/travel_time_model.pkl")

# === Sample user input (you can modify this or take actual input later) ===
user_input = {
    "Day_Of_Week": "Thursday",
    "Time_Of_Day": "08:30",
    "Trip_Type": "Home_to_Office",
    "Start_Lat": 12.9352,
    "Start_Lon": 77.6145,
    "End_Lat": 12.9716,
    "End_Lon": 77.5946,
    "Distance_KM": 8.5
}

# === Convert time to minutes ===
def convert_time_to_minutes(time_str):
    hour, minute = map(int, time_str.split(":"))
    return hour * 60 + minute

# === Convert speed category ===
# Just estimating based on urban average speeds
def estimate_speed_category(distance_km, time_min):
    speed = distance_km / (time_min / 60)
    if speed <= 20:
        return 0
    elif speed <= 40:
        return 1
    elif speed <= 60:
        return 2
    else:
        return 3

# Convert fields
time_minutes = convert_time_to_minutes(user_input["Time_Of_Day"])
day_index = pd.Categorical(
    [user_input["Day_Of_Week"]],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True
).codes[0]

trip_code = 0 if user_input["Trip_Type"] == "Home_to_Office" else 1

# Estimate average speed for this trip type (this is a logical assumption)
estimated_speed_kmph = 25 if trip_code == 0 else 30  # Office to home slightly faster
estimated_time = user_input["Distance_KM"] / estimated_speed_kmph * 60
speed_category = estimate_speed_category(user_input["Distance_KM"], estimated_time)

# === Prepare input for model ===
input_df = pd.DataFrame([{
    "Distance_KM": user_input["Distance_KM"],
    "Time_Minutes": time_minutes,
    "Day_Index": day_index,
    "Trip_Type_Code": trip_code,
    "Start_Lat": user_input["Start_Lat"],
    "Start_Lon": user_input["Start_Lon"],
    "End_Lat": user_input["End_Lat"],
    "End_Lon": user_input["End_Lon"],
    "Speed_Category": speed_category
}])

# === Predict ===
prediction = model.predict(input_df)[0]
print("🧠 Predicted Travel Time:", round(prediction, 2), "minutes")
