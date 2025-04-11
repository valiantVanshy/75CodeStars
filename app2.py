import pandas as pd
import joblib
import streamlit as st
from datetime import datetime
import math

# Load trained model and feature list
model = joblib.load("eta_predictor_model.pkl")
feature_cols = joblib.load("feature_columns.pkl")

st.title("🛣️ Travel Time Predictor")

st.markdown("Enter coordinates of origin and destination to predict estimated travel time.")

# User inputs: coordinates
from_lat = st.number_input("From Latitude", value=12.9716, format="%.6f")
from_lon = st.number_input("From Longitude", value=77.5946, format="%.6f")
to_lat = st.number_input("To Latitude", value=12.9352, format="%.6f")
to_lon = st.number_input("To Longitude", value=77.6146, format="%.6f")

# Use current time
now = datetime.now()
hour = now.hour
day_of_week = now.strftime("%A")

st.markdown(f"**Using Current Time:** {now.strftime('%H:%M')} on {day_of_week}")

# Haversine formula to compute distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Calculate road distance
raw_distance = haversine(from_lat, from_lon, to_lat, to_lon)
distance_km = round(raw_distance * 1.4, 2)

# Build input for model
input_data = {
    "distance_km": distance_km,
    "hour": hour,
    "trip_type_encoded": 1  # default (can change if model needs 0/1)
}

# Add missing day_of_week columns
day_dummies = {f"day_of_week_{day}": 0 for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'] if f"day_of_week_{day}" in feature_cols}
if f"day_of_week_{day_of_week}" in day_dummies:
    day_dummies[f"day_of_week_{day_of_week}"] = 1

input_data.update(day_dummies)

# Ensure all feature columns are present
for col in feature_cols:
    if col not in input_data:
        input_data[col] = 0

# Prepare for prediction
input_df = pd.DataFrame([input_data])[feature_cols]

if st.button("Predict ETA"):
    eta = model.predict(input_df)[0]
    st.success(f"⏱️ Estimated Travel Time: **{eta:.2f} minutes**")
