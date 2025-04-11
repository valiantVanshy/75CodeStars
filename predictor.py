import streamlit as st
import joblib
import pandas as pd
from datetime import datetime

# Load the trained model
model = joblib.load("commute_eta_predictor.pkl")

# App title
st.title("🚗 Commute Time Predictor")
st.markdown("Enter your commute details to predict travel time (ETA)")

# Inputs from user
distance_km = st.slider("Distance (km)", 1.0, 50.0, step=0.5)
day_of_week = st.selectbox("Day of Week", [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
])
hour = st.slider("Hour of Day", 0, 23)
direction = st.radio("Direction", ["Home→Office", "Office→Home"])

# Convert inputs
day_map = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}
day_num = day_map[day_of_week]
direction_flag = 1 if direction == "Home→Office" else 0

# Predict button
if st.button("Predict ETA"):
    input_data = pd.DataFrame([{
        "distance_km": distance_km,
        "day_of_week": day_num,
        "hour": hour,
        "direction_flag": direction_flag
    }])

    prediction = model.predict(input_data)[0]
    st.success(f"🕒 Estimated Travel Time: {prediction:.2f} minutes")
