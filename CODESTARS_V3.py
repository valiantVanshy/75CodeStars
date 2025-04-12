import pandas as pd
import joblib
import streamlit as st
from datetime import datetime
import math
import pydeck as pdk

# --- Load Model & Features ---
model = joblib.load("eta_predictor_model.pkl")
feature_cols = joblib.load("feature_columns.pkl")

# --- Page Config ---
st.set_page_config(page_title="ETA Predictor", page_icon="🛣️", layout="centered")

# --- Main Title ---
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>🛣️ Commute Time Predictor</h1>
    <p style='text-align: center; color: #7F8C8D; font-size:18px;'>
        Estimate commute duration based on coordinates, time, and weekday
    </p>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("👥 Team Members")
st.sidebar.markdown("""
- **Chirantana K M** 🎓  
- **Vanshika Sharma** 🧠  
- **Venkata Bhanuteja Yadalla** 💻  
- **Jonathan Samuel Jason** 📊  
""")
st.sidebar.markdown("---")
st.sidebar.info("🚗 ETA Prediction App - April 2025")

# --- Input Section ---
st.markdown("### 📍 Enter Trip Details")

col1, col2 = st.columns(2)
with col1:
    from_lat = st.number_input("From Latitude", value=12.9716, format="%.6f")
    from_lon = st.number_input("From Longitude", value=77.5946, format="%.6f")
with col2:
    to_lat = st.number_input("To Latitude", value=12.9352, format="%.6f")
    to_lon = st.number_input("To Longitude", value=77.6146, format="%.6f")

# Trip Type Dropdown
trip_type = st.selectbox("Trip Type", ["Home to Office", "Office to Home"])
trip_type_encoded = 1 if trip_type == "Home to Office" else 0

# --- Date & Time Display ---
now = datetime.now()
hour = now.hour
day_of_week = now.strftime("%A")
st.markdown(f"""
<div style="background-color:#F0F8FF; padding: 10px 20px; border-radius: 10px; font-size:16px;">
    🕒 <b>Current Time:</b> {now.strftime('%H:%M')} &nbsp;&nbsp; | &nbsp;&nbsp; 📅 <b>Today:</b> {day_of_week}
</div>
""", unsafe_allow_html=True)

# --- Distance Calculation ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

raw_distance = haversine(from_lat, from_lon, to_lat, to_lon)
distance_km = round(raw_distance * 1.4, 2)

# --- Input Data ---
input_data = {
    "distance_km": distance_km,
    "hour": hour,
    "trip_type_encoded": trip_type_encoded
}

day_dummies = {f"day_of_week_{day}": 0 for day in ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
if f"day_of_week_{day_of_week}" in day_dummies:
    day_dummies[f"day_of_week_{day_of_week}"] = 1

input_data.update(day_dummies)
for col in feature_cols:
    if col not in input_data:
        input_data[col] = 0

input_df = pd.DataFrame([input_data])[feature_cols]

# --- Map ---
st.markdown("### 🗺️ Route Map")
map_df = pd.DataFrame([
    {"lat": from_lat, "lon": from_lon, "label": "Start"},
    {"lat": to_lat, "lon": to_lon, "label": "End"}
])
st.map(map_df)

# --- Predict Button ---
st.markdown("### 🚀 Get Estimated Travel Time")
if st.button("Predict ETA"):
    try:
        eta = model.predict(input_df)[0]
        st.success(f"⏱️ **Estimated Travel Time: {eta:.2f} minutes**")
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
